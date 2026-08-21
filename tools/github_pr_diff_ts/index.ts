/**
 * GitHub PR Code Review Diff Tool for AI Agents & MCP Hub.
 *
 * Fetches pull request metadata, per-file patches, and raw unified diffs from
 * the GitHub REST API so an LLM can perform automated code review.
 *
 * Uses the native `fetch` API (Node.js 18+) — no runtime dependencies.
 */

interface PullRequestMeta {
  number: number;
  title: string;
  state: string;
  draft: boolean;
  author: string | null;
  base_branch: string;
  head_branch: string;
  head_sha: string;
  additions: number;
  deletions: number;
  changed_files: number;
  body: string | null;
  html_url: string;
}

interface ChangedFile {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  changes: number;
  patch: string | null;
  patch_truncated: boolean;
  previous_filename?: string;
  binary: boolean;
}

interface ToolResult {
  success: boolean;
  action?: string;
  repository?: string;
  pull_request?: PullRequestMeta;
  files?: ChangedFile[];
  files_returned?: number;
  files_omitted?: number;
  diff?: string;
  diff_truncated?: boolean;
  review_prompt?: string;
  rate_limit_remaining?: number | null;
  error?: string;
}

interface RequestOptions {
  github_token?: string;
  accept?: string;
}

const GITHUB_API = "https://api.github.com";
const DEFAULT_MAX_PATCH_CHARS = 6000;
const DEFAULT_MAX_FILES = 100;
const PER_PAGE = 100;

/**
 * Files that add diff noise without adding review value. Skipped by default so
 * a lockfile refresh does not consume the model's context window.
 */
const DEFAULT_EXCLUDE_PATTERNS = [
  "package-lock.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  "poetry.lock",
  "Cargo.lock",
  "go.sum",
  "*.min.js",
  "*.min.css",
  "*.map",
];

/**
 * Parses a pull request URL such as
 * https://github.com/owner/repo/pull/123 into its components.
 */
function parsePullRequestUrl(
  url: string
): { owner: string; repo: string; pull_number: number } | null {
  const match = url
    .trim()
    .match(/github\.com\/([^/\s]+)\/([^/\s]+)\/pull\/(\d+)/i);
  if (!match) {
    return null;
  }
  return {
    owner: match[1],
    repo: match[2].replace(/\.git$/, ""),
    pull_number: Number(match[3]),
  };
}

/**
 * Matches a filename against a shell-style glob (supports `*` only), which is
 * all the exclude patterns need.
 */
function matchesPattern(filename: string, pattern: string): boolean {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*/g, ".*");
  const regex = new RegExp(`(^|/)${escaped}$`, "i");
  return regex.test(filename);
}

function buildHeaders(options: RequestOptions = {}): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: options.accept || "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "agent-tools-mcp-hub-github-pr-diff",
  };

  const token = options.github_token || process.env.GITHUB_TOKEN;
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

/**
 * Translates a non-OK GitHub response into an actionable error message.
 * Rate limiting and missing-token cases are called out explicitly because they
 * are by far the most common failure for unauthenticated agents.
 */
async function describeHttpError(
  response: Response,
  context: string
): Promise<string> {
  const remaining = response.headers.get("x-ratelimit-remaining");
  const hasToken = Boolean(process.env.GITHUB_TOKEN);

  if (response.status === 403 && remaining === "0") {
    const resetHeader = response.headers.get("x-ratelimit-reset");
    const resetsAt = resetHeader
      ? new Date(Number(resetHeader) * 1000).toISOString()
      : "unknown";
    return (
      `GitHub API rate limit exceeded (resets at ${resetsAt}). ` +
      (hasToken
        ? "Authenticated limit is 5000 requests/hour."
        : "Set the GITHUB_TOKEN environment variable to raise the limit from 60 to 5000 requests/hour.")
    );
  }

  if (response.status === 404) {
    return (
      `${context} not found (404). Check the owner, repo, and pull request number. ` +
      (hasToken
        ? "For private repositories, confirm the token has 'repo' scope."
        : "Private repositories require a GITHUB_TOKEN with 'repo' scope.")
    );
  }

  if (response.status === 401) {
    return "GitHub authentication failed (401). The provided GITHUB_TOKEN is invalid or expired.";
  }

  let detail = "";
  try {
    const body = (await response.json()) as { message?: string };
    detail = body.message ? ` — ${body.message}` : "";
  } catch {
    detail = "";
  }

  return `GitHub API error while fetching ${context}: ${response.status} ${response.statusText}${detail}`;
}

/**
 * Fetches metadata for a single pull request: title, author, branches, and
 * aggregate change counts.
 */
async function getPullRequest(
  owner: string,
  repo: string,
  pull_number: number,
  options: RequestOptions = {}
): Promise<ToolResult> {
  const validation = validateTarget(owner, repo, pull_number);
  if (validation) {
    return { success: false, error: validation };
  }

  try {
    const response = await fetch(
      `${GITHUB_API}/repos/${owner}/${repo}/pulls/${pull_number}`,
      { headers: buildHeaders(options) }
    );

    if (!response.ok) {
      return {
        success: false,
        error: await describeHttpError(
          response,
          `pull request ${owner}/${repo}#${pull_number}`
        ),
      };
    }

    const pr = (await response.json()) as Record<string, any>;

    return {
      success: true,
      action: "metadata",
      repository: `${owner}/${repo}`,
      pull_request: normalizePullRequest(pr),
      rate_limit_remaining: readRateLimit(response),
    };
  } catch (err) {
    return { success: false, error: describeUnexpected(err) };
  }
}

/**
 * Fetches the changed files of a pull request with their unified patches.
 *
 * Handles pagination (GitHub caps at 100 files per page), skips noisy generated
 * files, and truncates oversized patches so the payload stays inside an LLM
 * context window.
 */
async function getPullRequestFiles(
  owner: string,
  repo: string,
  pull_number: number,
  options: {
    max_files?: number;
    max_patch_chars?: number;
    include_patch?: boolean;
    exclude_patterns?: string[];
    github_token?: string;
  } = {}
): Promise<ToolResult> {
  const validation = validateTarget(owner, repo, pull_number);
  if (validation) {
    return { success: false, error: validation };
  }

  const maxFiles = clamp(options.max_files ?? DEFAULT_MAX_FILES, 1, 300);
  const maxPatchChars = clamp(
    options.max_patch_chars ?? DEFAULT_MAX_PATCH_CHARS,
    200,
    100000
  );
  const includePatch = options.include_patch ?? true;
  const excludePatterns = options.exclude_patterns ?? DEFAULT_EXCLUDE_PATTERNS;

  try {
    const collected: Record<string, any>[] = [];
    let page = 1;
    let rateLimit: number | null = null;

    // Paginate until GitHub returns a short page or we have enough files.
    while (collected.length < maxFiles) {
      const response = await fetch(
        `${GITHUB_API}/repos/${owner}/${repo}/pulls/${pull_number}/files` +
          `?per_page=${PER_PAGE}&page=${page}`,
        { headers: buildHeaders(options) }
      );

      if (!response.ok) {
        return {
          success: false,
          error: await describeHttpError(
            response,
            `files for pull request ${owner}/${repo}#${pull_number}`
          ),
        };
      }

      rateLimit = readRateLimit(response);
      const batch = (await response.json()) as Record<string, any>[];
      collected.push(...batch);

      if (batch.length < PER_PAGE) {
        break;
      }
      page += 1;
    }

    const excluded = collected.filter((file) =>
      excludePatterns.some((pattern) => matchesPattern(file.filename, pattern))
    );
    const relevant = collected.filter((file) => !excluded.includes(file));
    const selected = relevant.slice(0, maxFiles);

    const files: ChangedFile[] = selected.map((file) =>
      normalizeFile(file, includePatch, maxPatchChars)
    );

    return {
      success: true,
      action: "files",
      repository: `${owner}/${repo}`,
      files,
      files_returned: files.length,
      files_omitted: collected.length - files.length,
      rate_limit_remaining: rateLimit,
    };
  } catch (err) {
    return { success: false, error: describeUnexpected(err) };
  }
}

/**
 * Fetches the raw unified diff for a pull request as a single string, using the
 * `application/vnd.github.v3.diff` media type.
 */
async function getPullRequestDiff(
  owner: string,
  repo: string,
  pull_number: number,
  options: { max_diff_chars?: number; github_token?: string } = {}
): Promise<ToolResult> {
  const validation = validateTarget(owner, repo, pull_number);
  if (validation) {
    return { success: false, error: validation };
  }

  const maxDiffChars = clamp(options.max_diff_chars ?? 100000, 500, 1000000);

  try {
    const response = await fetch(
      `${GITHUB_API}/repos/${owner}/${repo}/pulls/${pull_number}`,
      {
        headers: buildHeaders({
          github_token: options.github_token,
          accept: "application/vnd.github.v3.diff",
        }),
      }
    );

    if (!response.ok) {
      return {
        success: false,
        error: await describeHttpError(
          response,
          `diff for pull request ${owner}/${repo}#${pull_number}`
        ),
      };
    }

    const raw = await response.text();
    const truncated = raw.length > maxDiffChars;

    return {
      success: true,
      action: "diff",
      repository: `${owner}/${repo}`,
      diff: truncated
        ? `${raw.slice(0, maxDiffChars)}\n... [diff truncated at ${maxDiffChars} characters]`
        : raw,
      diff_truncated: truncated,
      rate_limit_remaining: readRateLimit(response),
    };
  } catch (err) {
    return { success: false, error: describeUnexpected(err) };
  }
}

/**
 * Builds a single review-ready payload: PR metadata, the changed files with
 * their patches, and a formatted prompt an agent can hand straight to an LLM.
 */
async function getReviewContext(
  owner: string,
  repo: string,
  pull_number: number,
  options: {
    max_files?: number;
    max_patch_chars?: number;
    exclude_patterns?: string[];
    github_token?: string;
  } = {}
): Promise<ToolResult> {
  const meta = await getPullRequest(owner, repo, pull_number, options);
  if (!meta.success) {
    return meta;
  }

  const filesResult = await getPullRequestFiles(
    owner,
    repo,
    pull_number,
    options
  );
  if (!filesResult.success) {
    return filesResult;
  }

  const pr = meta.pull_request as PullRequestMeta;
  const files = filesResult.files as ChangedFile[];

  const sections = files.map((file) => {
    const header = `### ${file.filename} (${file.status}, +${file.additions}/-${file.deletions})`;
    if (file.binary) {
      return `${header}\n[binary file — no textual diff]`;
    }
    if (!file.patch) {
      return `${header}\n[patch unavailable]`;
    }
    return `${header}\n\`\`\`diff\n${file.patch}\n\`\`\``;
  });

  const reviewPrompt = [
    `Review pull request #${pr.number} in ${owner}/${repo}.`,
    ``,
    `Title: ${pr.title}`,
    `Author: ${pr.author ?? "unknown"}`,
    `Target: ${pr.head_branch} -> ${pr.base_branch}`,
    `Scope: ${pr.changed_files} file(s), +${pr.additions}/-${pr.deletions}`,
    ``,
    `Description:`,
    pr.body?.trim() || "(no description provided)",
    ``,
    `Changed files:`,
    ``,
    sections.join("\n\n"),
  ].join("\n");

  return {
    success: true,
    action: "review_context",
    repository: `${owner}/${repo}`,
    pull_request: pr,
    files,
    files_returned: files.length,
    files_omitted: filesResult.files_omitted,
    review_prompt: reviewPrompt,
    rate_limit_remaining: filesResult.rate_limit_remaining,
  };
}

function normalizePullRequest(pr: Record<string, any>): PullRequestMeta {
  return {
    number: pr.number,
    title: pr.title,
    state: pr.state,
    draft: Boolean(pr.draft),
    author: pr.user?.login ?? null,
    base_branch: pr.base?.ref ?? "",
    head_branch: pr.head?.ref ?? "",
    head_sha: pr.head?.sha ?? "",
    additions: pr.additions ?? 0,
    deletions: pr.deletions ?? 0,
    changed_files: pr.changed_files ?? 0,
    body: pr.body ?? null,
    html_url: pr.html_url ?? "",
  };
}

function normalizeFile(
  file: Record<string, any>,
  includePatch: boolean,
  maxPatchChars: number
): ChangedFile {
  // GitHub omits `patch` for binary files and for individual files whose diff
  // exceeds its internal size cap.
  const rawPatch: string | undefined = file.patch;
  let patch: string | null = null;
  let patchTruncated = false;

  if (includePatch && typeof rawPatch === "string") {
    if (rawPatch.length > maxPatchChars) {
      patch = `${rawPatch.slice(0, maxPatchChars)}\n... [patch truncated at ${maxPatchChars} characters]`;
      patchTruncated = true;
    } else {
      patch = rawPatch;
    }
  }

  const normalized: ChangedFile = {
    filename: file.filename,
    status: file.status,
    additions: file.additions ?? 0,
    deletions: file.deletions ?? 0,
    changes: file.changes ?? 0,
    patch,
    patch_truncated: patchTruncated,
    binary: typeof rawPatch !== "string" && (file.changes ?? 0) === 0,
  };

  if (file.previous_filename) {
    normalized.previous_filename = file.previous_filename;
  }

  return normalized;
}

function validateTarget(
  owner: string,
  repo: string,
  pull_number: number
): string | null {
  if (!owner || !owner.trim()) {
    return "Repository owner is required.";
  }
  if (!repo || !repo.trim()) {
    return "Repository name is required.";
  }
  if (!Number.isInteger(pull_number) || pull_number < 1) {
    return "Pull request number must be a positive integer.";
  }
  return null;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function readRateLimit(response: Response): number | null {
  const remaining = response.headers.get("x-ratelimit-remaining");
  return remaining === null ? null : Number(remaining);
}

function describeUnexpected(err: unknown): string {
  const message = err instanceof Error ? err.message : String(err);
  return `Unexpected error contacting the GitHub API: ${message}`;
}

/**
 * Main dispatcher entrypoint for agent frameworks.
 *
 * Accepts either an explicit owner/repo/pull_number triple or a `pr_url`,
 * since agents frequently hold only the pull request link.
 */
async function runTool(
  action: string,
  options: Record<string, any> = {}
): Promise<ToolResult> {
  let { owner, repo, pull_number } = options;

  if (options.pr_url) {
    const parsed = parsePullRequestUrl(options.pr_url);
    if (!parsed) {
      return {
        success: false,
        error:
          "Could not parse pr_url. Expected a URL like https://github.com/owner/repo/pull/123",
      };
    }
    owner = parsed.owner;
    repo = parsed.repo;
    pull_number = parsed.pull_number;
  }

  switch (action) {
    case "metadata":
      return getPullRequest(owner, repo, pull_number, options);
    case "files":
      return getPullRequestFiles(owner, repo, pull_number, options);
    case "diff":
      return getPullRequestDiff(owner, repo, pull_number, options);
    case "review_context":
      return getReviewContext(owner, repo, pull_number, options);
    default:
      return {
        success: false,
        error: `Invalid action '${action}'. Must be one of: 'metadata', 'files', 'diff', 'review_context'.`,
      };
  }
}

export {
  getPullRequest,
  getPullRequestFiles,
  getPullRequestDiff,
  getReviewContext,
  parsePullRequestUrl,
  runTool,
};

// Self-test when run directly (`npm start`), not when imported as a module.
if (require.main === module) {
  (async () => {
    console.log("GitHub PR Code Review Diff Tool loaded.");
    console.log(
      "Set GITHUB_TOKEN to raise the rate limit from 60 to 5000 requests/hour.\n"
    );

    const result = await runTool("review_context", {
      pr_url: "https://github.com/tarunjandra/agent-tools-mcp-hub/pull/68",
      max_files: 3,
      max_patch_chars: 400,
    });

    if (result.success) {
      console.log(`Repository:    ${result.repository}`);
      console.log(`Pull request:  #${result.pull_request?.number} ${result.pull_request?.title}`);
      console.log(`Author:        ${result.pull_request?.author}`);
      console.log(`Changed files: ${result.pull_request?.changed_files}`);
      console.log(`Files fetched: ${result.files_returned} (omitted ${result.files_omitted})`);
      console.log(`Rate limit:    ${result.rate_limit_remaining} remaining\n`);
      console.log("--- review_prompt preview ---");
      console.log(`${result.review_prompt?.slice(0, 600)}\n...`);
    } else {
      console.log(JSON.stringify(result, null, 2));
    }
  })();
}

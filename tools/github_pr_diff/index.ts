/**
 * GitHub PR Code Review Diff Tool for AI Agents & MCP Hub.
 * Fetches diff files and patch details for any pull request to enable
 * automated AI code reviews via the GitHub REST API.
 */

const GITHUB_API = "https://api.github.com";
const USER_AGENT = "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)";

interface PullRequestMeta {
  number: number;
  title: string;
  state: string;
  author: string;
  base: string;
  head: string;
  mergeable: boolean | null;
  created_at: string;
  updated_at: string;
  html_url: string;
  additions: number;
  deletions: number;
  changed_files: number;
}

interface FileDiff {
  filename: string;
  status: string;
  additions: number;
  deletions: number;
  changes: number;
  patch?: string;
  blob_url: string;
  raw_url: string;
  previous_filename?: string;
}

interface DiffResult {
  success: boolean;
  pull_request?: PullRequestMeta;
  files?: FileDiff[];
  file_count?: number;
  error?: string;
}

interface ReviewComment {
  id: number;
  path: string;
  body: string;
  user: string;
  created_at: string;
  line?: number | null;
  side?: string;
}

interface CommentsResult {
  success: boolean;
  pull_request_number?: number;
  comments?: ReviewComment[];
  count?: number;
  error?: string;
}

async function githubFetch(
  endpoint: string,
  token?: string,
  accept?: string
): Promise<{ data?: any; error?: string; status?: number }> {
  const headers: Record<string, string> = {
    "User-Agent": USER_AGENT,
    Accept: accept || "application/vnd.github+json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${GITHUB_API}${endpoint}`, { headers });

    if (!response.ok) {
      if (response.status === 404) {
        return { error: "Repository or pull request not found.", status: 404 };
      }
      if (response.status === 403 && (await response.text()).toLowerCase().includes("rate limit")) {
        return {
          error: "GitHub API rate limit reached. Set GITHUB_TOKEN to raise the limit.",
          status: 403,
        };
      }
      return {
        error: `GitHub API returned status ${response.status}: ${response.statusText}`,
        status: response.status,
      };
    }

    const data = await response.json();
    return { data };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return { error: `Network error contacting GitHub: ${message}` };
  }
}

function parseRepo(repo: string): { owner: string; repo: string } | null {
  const cleaned = repo.trim().replace(/^https?:\/\/github\.com\//, "").replace(/\/$/, "");
  const parts = cleaned.split("/");
  if (parts.length < 2 || !parts[0] || !parts[1]) {
    return null;
  }
  return { owner: parts[0], repo: parts[1] };
}

/**
 * Fetches PR metadata and the list of changed files with their patches.
 */
async function getPRDiff(
  repo: string,
  pr_number: number,
  options: {
    include_patch?: boolean;
    token?: string;
  } = {}
): Promise<DiffResult> {
  if (!repo) {
    return { success: false, error: "Repository is required in 'owner/repo' format." };
  }

  const parsed = parseRepo(repo);
  if (!parsed) {
    return { success: false, error: "Repository must be in 'owner/repo' format, e.g. 'facebook/react'." };
  }

  if (!pr_number || pr_number < 1) {
    return { success: false, error: "A valid pull request number is required." };
  }

  const token = options.token || process.env.GITHUB_TOKEN;
  const { owner, repo: repoName } = parsed;

  const prResult = await githubFetch(`/repos/${owner}/${repoName}/pulls/${pr_number}`, token);
  if (prResult.error) {
    return { success: false, error: prResult.error };
  }

  const pr = prResult.data;
  const prMeta: PullRequestMeta = {
    number: pr.number,
    title: pr.title,
    state: pr.state,
    author: pr.user?.login || "",
    base: pr.base?.ref || "",
    head: pr.head?.ref || "",
    mergeable: pr.mergeable,
    created_at: pr.created_at,
    updated_at: pr.updated_at,
    html_url: pr.html_url,
    additions: pr.additions,
    deletions: pr.deletions,
    changed_files: pr.changed_files,
  };

  const filesResult = await githubFetch(
    `/repos/${owner}/${repoName}/pulls/${pr_number}/files?per_page=100`,
    token
  );
  if (filesResult.error) {
    return { success: false, error: filesResult.error };
  }

  const includePatch = options.include_patch !== false;
  const files: FileDiff[] = (filesResult.data || []).map((f: any) => {
    const file: FileDiff = {
      filename: f.filename,
      status: f.status,
      additions: f.additions,
      deletions: f.deletions,
      changes: f.changes,
      blob_url: f.blob_url,
      raw_url: f.raw_url,
    };
    if (includePatch && f.patch) {
      file.patch = f.patch;
    }
    if (f.previous_filename) {
      file.previous_filename = f.previous_filename;
    }
    return file;
  });

  return {
    success: true,
    pull_request: prMeta,
    files,
    file_count: files.length,
  };
}

/**
 * Fetches review comments on a pull request.
 */
async function getPRComments(
  repo: string,
  pr_number: number,
  options: {
    token?: string;
  } = {}
): Promise<CommentsResult> {
  if (!repo) {
    return { success: false, error: "Repository is required in 'owner/repo' format." };
  }

  const parsed = parseRepo(repo);
  if (!parsed) {
    return { success: false, error: "Repository must be in 'owner/repo' format." };
  }

  if (!pr_number || pr_number < 1) {
    return { success: false, error: "A valid pull request number is required." };
  }

  const token = options.token || process.env.GITHUB_TOKEN;
  const { owner, repo: repoName } = parsed;

  const result = await githubFetch(
    `/repos/${owner}/${repoName}/pulls/${pr_number}/comments?per_page=100`,
    token
  );
  if (result.error) {
    return { success: false, error: result.error };
  }

  const comments: ReviewComment[] = (result.data || []).map((c: any) => ({
    id: c.id,
    path: c.path,
    body: c.body,
    user: c.user?.login || "",
    created_at: c.created_at,
    line: c.line || c.original_line || null,
    side: c.side || undefined,
  }));

  return {
    success: true,
    pull_request_number: pr_number,
    comments,
    count: comments.length,
  };
}

/**
 * Main dispatcher entrypoint for agent frameworks.
 */
async function runTool(
  action: string,
  repo: string,
  pr_number: number,
  options: Record<string, any> = {}
): Promise<DiffResult | CommentsResult> {
  switch (action) {
    case "diff":
      return getPRDiff(repo, pr_number, options);
    case "comments":
      return getPRComments(repo, pr_number, options);
    default:
      return {
        success: false,
        error: `Invalid action '${action}'. Must be 'diff' or 'comments'.`,
      };
  }
}

export { getPRDiff, getPRComments, runTool };

// Self-test when run directly
(async () => {
  console.log("GitHub PR Code Review Diff Tool loaded.");
  console.log("Set GITHUB_TOKEN for higher rate limits (optional for public repos).\n");
  console.log("Fetching diff for tarunjandra/agent-tools-mcp-hub PR #57:");
  const result = await getPRDiff("tarunjandra/agent-tools-mcp-hub", 57, {
    include_patch: false,
  });
  console.log(JSON.stringify(result, null, 2));
})();

# GitHub PR Code Review Diff Tool

Fetches pull request metadata, per-file patches, and raw unified diffs from the GitHub REST API so an AI agent can perform automated code review.

Built with the native `fetch` API (Node.js 18+) — **zero runtime dependencies**.

## Why this tool

Feeding a pull request to an LLM sounds trivial until you hit the real diffs: a 300-file PR paginates, a refreshed `package-lock.json` alone can blow the context window, and a single vendored bundle can be larger than the entire code change. This tool handles those cases so the agent receives a payload that actually fits:

- **Pagination** — the GitHub files endpoint caps at 100 per page; this walks the pages for you.
- **Generated-file filtering** — lockfiles and minified assets are skipped by default.
- **Patch truncation** — per-file and whole-diff caps, with an explicit `patch_truncated` flag so the model is never silently misled about what it is reviewing.
- **Binary awareness** — binary files are flagged rather than emitted as an empty patch.

## Actions

| Action | Returns |
| :--- | :--- |
| `metadata` | PR title, author, state, branches, and aggregate change counts |
| `files` | Changed files with status, line counts, and unified patches |
| `diff` | The raw unified diff as a single string |
| `review_context` | Metadata + files + a formatted `review_prompt` ready to send to an LLM |

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `action` | `string` | Yes | `metadata`, `files`, `diff`, or `review_context` |
| `pr_url` | `string` | No\* | Full PR URL, e.g. `https://github.com/owner/repo/pull/123`. Overrides the three fields below. |
| `owner` | `string` | No\* | Repository owner or organization |
| `repo` | `string` | No\* | Repository name |
| `pull_number` | `integer` | No\* | Pull request number |
| `max_files` | `integer` | No | Max changed files to return (1–300, default 100) |
| `max_patch_chars` | `integer` | No | Max characters per file patch (200–100000, default 6000) |
| `max_diff_chars` | `integer` | No | Max characters for the raw diff (500–1000000, default 100000) |
| `include_patch` | `boolean` | No | Include patch bodies. Set `false` for a lightweight filename-only summary. Default `true`. |
| `exclude_patterns` | `string[]` | No | Glob patterns to skip. Defaults to lockfiles and minified assets. |
| `github_token` | `string` | No | Falls back to `GITHUB_TOKEN`. Optional for public repositories. |

\* Supply **either** `pr_url` **or** all of `owner` + `repo` + `pull_number`.

## Installation & Setup

```bash
cd tools/github_pr_diff_ts
npm install
npm start          # runs the built-in self-test against a live public PR
```

Public repositories work with no credentials at all (GitHub allows 60 requests/hour unauthenticated). To raise the limit to 5000/hour, or to read private repositories, set a token:

```bash
export GITHUB_TOKEN="ghp_your_token_here"   # never hardcode this
```

A fine-grained token needs **Pull requests: read-only**; a classic token needs the `repo` scope for private repositories.

## Usage Example

```typescript
import { runTool } from "./index";

// Build an LLM-ready review payload from a PR URL
const result = await runTool("review_context", {
  pr_url: "https://github.com/tarunjandra/agent-tools-mcp-hub/pull/68",
  max_files: 20,
  max_patch_chars: 4000,
});

if (result.success) {
  console.log(result.pull_request?.title);
  // Hand result.review_prompt straight to your model
  console.log(result.review_prompt);
} else {
  console.error(result.error);
}
```

### Fetching individual file patches

```typescript
import { getPullRequestFiles } from "./index";

const result = await getPullRequestFiles("tarunjandra", "agent-tools-mcp-hub", 68, {
  max_files: 2,
  max_patch_chars: 200,
});
```

Actual output:

```json
{
  "success": true,
  "action": "files",
  "repository": "tarunjandra/agent-tools-mcp-hub",
  "files": [
    {
      "filename": "tools/supabase_table_query/.gitignore",
      "status": "added",
      "additions": 3,
      "deletions": 0,
      "changes": 3,
      "patch": "@@ -0,0 +1,3 @@\n+node_modules/\n+dist/\n+.env",
      "patch_truncated": false,
      "binary": false
    },
    {
      "filename": "tools/supabase_table_query/README.md",
      "status": "added",
      "additions": 84,
      "deletions": 0,
      "changes": 84,
      "patch": "@@ -0,0 +1,84 @@\n+# Supabase Realtime Table Query Tool\n... [patch truncated at 200 characters]",
      "patch_truncated": true,
      "binary": false
    }
  ],
  "files_returned": 2,
  "files_omitted": 5,
  "rate_limit_remaining": 55
}
```

### Raw unified diff

```typescript
import { getPullRequestDiff } from "./index";

const { diff } = await getPullRequestDiff("tarunjandra", "agent-tools-mcp-hub", 68);
```

## Error Handling

Every function resolves to `{ success: false, error }` rather than throwing, so an agent loop never crashes on a bad tool call. Common failures return actionable messages:

| Situation | Message |
| :--- | :--- |
| Rate limit exhausted | Reports the reset time and how to raise the limit |
| PR or repo not found | Explains the 404 and notes that private repos need a token |
| Invalid/expired token | Reports the 401 explicitly |
| Malformed `pr_url` | Shows the expected URL shape |
| Unknown `action` | Lists the valid actions |

Each successful response also carries `rate_limit_remaining` so an agent can back off before it gets throttled.

## MCP / Agent Integration

`runTool(action, options)` is the single dispatcher entrypoint, and `metadata.json` describes the input schema in JSON Schema form — so the tool maps directly onto MCP tool definitions, OpenAI function calling, and LangChain `StructuredTool` wrappers.

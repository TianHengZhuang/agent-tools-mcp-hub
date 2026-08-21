# GitHub PR Code Review Diff Tool

Fetch diff files and patch details for any GitHub pull request to enable automated AI code reviews. Also retrieves review comments for a PR.

> Closes [#45](https://github.com/tarunjandra/agent-tools-mcp-hub/issues/45)

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `action` | `string` | No | `"diff"` for changed files & patches, `"comments"` for review comments (default `"diff"`) |
| `repo` | `string` | **Yes** | Repository in `owner/repo` format |
| `pr_number` | `integer` | **Yes** | Pull request number |
| `include_patch` | `boolean` | No | Include unified diff patch content per file (default `true`) |

## Environment Variables

| Variable | Description |
| :--- | :--- |
| `GITHUB_TOKEN` | Optional. A GitHub personal access token. Not required for public repos but raises rate limits. |

## Installation & Setup

```bash
cd tools/github_pr_diff
npm install
```

## Usage Examples

### Fetch PR diff (changed files & patches)

```typescript
import { getPRDiff } from "./index";

const result = await getPRDiff("facebook/react", 28000, {
  include_patch: true,
});
console.log(result);
// {
//   success: true,
//   pull_request: { number, title, state, author, additions, deletions, ... },
//   files: [{ filename, status, additions, deletions, patch, ... }],
//   file_count: 5
// }
```

### Fetch PR review comments

```typescript
import { getPRComments } from "./index";

const result = await getPRComments("facebook/react", 28000);
console.log(result);
// {
//   success: true,
//   pull_request_number: 28000,
//   comments: [{ id, path, body, user, line, ... }],
//   count: 12
// }
```

### Using the dispatcher

```typescript
import { runTool } from "./index";

const diff = await runTool("diff", "owner/repo", 42);
const comments = await runTool("comments", "owner/repo", 42);
```

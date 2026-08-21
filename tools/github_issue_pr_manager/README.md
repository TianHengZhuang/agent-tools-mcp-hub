# GitHub Issue & PR Manager

A lightweight GitHub REST API connector for AI agents and MCP workflows.

This tool can:
- List repository issues
- List repository pull requests
- Create a new issue
- Create a comment on an issue or pull request

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `action` | `string` | Yes | One of: `list_issues`, `list_pull_requests`, `create_issue`, `create_issue_comment` |
| `repo` | `string` | Yes | Repository in `owner/repo` format |
| `state` | `string` | No | For list actions: `open`, `closed`, or `all` (default `open`) |
| `per_page` | `integer` | No | Number of list items per page (1-100, default 10) |
| `page` | `integer` | No | Page number for list actions (default 1) |
| `include_pull_requests` | `boolean` | No | For `list_issues`, include PR items from the issues endpoint |
| `title` | `string` | No | Required for `create_issue` |
| `body` | `string` | No | Optional issue body for `create_issue` |
| `issue_number` | `integer` | No | Required for `create_issue_comment` |
| `comment_body` | `string` | No | Required for `create_issue_comment` |
| `github_token` | `string` | No | Optional token override (defaults to `GITHUB_TOKEN`) |

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

For write actions (`create_issue`, `create_issue_comment`), set:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

## Usage Example

```python
from tool import run_tool

# 1) List issues
print(run_tool(
    action="list_issues",
    repo="tarunjandra/agent-tools-mcp-hub",
    state="open",
    per_page=5
))

# 2) List pull requests
print(run_tool(
    action="list_pull_requests",
    repo="tarunjandra/agent-tools-mcp-hub",
    state="open",
    per_page=5
))

# 3) Create issue (requires GITHUB_TOKEN)
print(run_tool(
    action="create_issue",
    repo="your-org/your-repo",
    title="Automated issue from connector",
    body="Created via github_issue_pr_manager tool."
))

# 4) Create comment (requires GITHUB_TOKEN)
print(run_tool(
    action="create_issue_comment",
    repo="your-org/your-repo",
    issue_number=123,
    comment_body="Automated comment from connector tool."
))
```

# GitHub Repository Info

Fetch public metadata for any GitHub repository — stars, forks, primary language, open issues, license, topics, homepage and description — using the public **GitHub REST API**.

- **No API key required.** An optional `GITHUB_TOKEN` environment variable raises the rate limit (60 → 5,000 requests/hour).
- Graceful handling of not-found repos, rate limits and network errors.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | yes | Repository in `owner/repo` format, e.g. `openai/openai-python` |

## Setup

```bash
pip install -r requirements.txt
# optional, to raise the rate limit:
export GITHUB_TOKEN="ghp_xxx"
```

## Usage

```python
from tool import run_tool

result = run_tool("tarunjandra/agent-tools-mcp-hub")
print(result)
```

### Example output

```json
{
  "success": true,
  "data": {
    "full_name": "tarunjandra/agent-tools-mcp-hub",
    "description": "Curated collection of modular AI agent tools and MCP server connectors.",
    "language": "Python",
    "stars": 3,
    "forks": 12,
    "open_issues": 30,
    "license": "MIT",
    "topics": [],
    "homepage": null,
    "url": "https://github.com/tarunjandra/agent-tools-mcp-hub",
    "last_pushed": "2026-08-20T10:04:11Z"
  }
}
```

On error the tool returns `{"success": false, "error": "<reason>"}` — for example when the repository does not exist or the API rate limit is reached.

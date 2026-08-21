# Brave Search Web Connector

Queries the [Brave Search API](https://api-dashboard.search.brave.com/) for privacy-first web
results. Returns clean titles, URLs, snippets and source hostnames, with optional freshness
filtering, localisation and an AI summarizer key.

Standard library only - no third-party dependencies.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | The web search query | - |
| `count` | `integer` | No | Number of results to return (1-20) | `5` |
| `country` | `string` | No | Two-letter country code for localisation | `US` |
| `search_lang` | `string` | No | Language code for the results | `en` |
| `safesearch` | `string` | No | Adult content filter: `off`, `moderate`, `strict` | `moderate` |
| `freshness` | `string` | No | `pd` (24h), `pw` (7d), `pm` (31d), `py` (1y) or `2024-01-01to2024-06-30` | - |
| `summary` | `boolean` | No | Also request an AI summarizer key (needs a plan that includes the Summarizer) | `false` |
| `api_key` | `string` | No | Subscription token; falls back to the environment variable | - |

## Environment Variables

| Variable | Required | Description |
| :--- | :--- | :--- |
| `BRAVE_SEARCH_API_KEY` | Yes | Subscription token from the Brave Search API dashboard. `BRAVE_API_KEY` is also accepted. |

Get a free key (2,000 queries/month) at <https://api-dashboard.search.brave.com/app/keys>.

## Installation & Setup

```bash
pip install -r requirements.txt   # no external packages needed
export BRAVE_SEARCH_API_KEY="your-subscription-token"
```

## Usage Example

```python
from tool import search_brave

result = search_brave(query="model context protocol spec", count=3, freshness="pm")

if result["success"]:
    for item in result["data"]["results"]:
        print(f"{item['title']} - {item['url']}")
        print(item["description"], "\n")
else:
    print("Error:", result["error"])
```

The generic agent entrypoint works too:

```python
from tool import run_tool

run_tool("best python http clients", count=5, country="IN", safesearch="strict")
```

## Response Shape

```json
{
  "success": true,
  "data": {
    "query": "model context protocol spec",
    "count": 3,
    "results": [
      {
        "title": "Specification - Model Context Protocol",
        "url": "https://modelcontextprotocol.io/specification",
        "description": "MCP is an open protocol that standardizes how applications provide context to LLMs.",
        "source": "modelcontextprotocol.io",
        "age": null,
        "extra_snippets": []
      }
    ]
  }
}
```

On failure the tool never raises - it returns `{"success": false, "error": "...", "status_code": 429}`.

## Error Handling

| Situation | Behaviour |
| :--- | :--- |
| Missing API key | `success: false` with a message naming the env var |
| Empty query | `success: false`, no request is made |
| Invalid token (401 / 422) | Brave's own `code` and `detail` are surfaced |
| Rate limit (429) | Explicit rate-limit message plus `status_code` |
| Network / timeout | `success: false` with the underlying reason (20s timeout) |
| No matches | `success: true` with `count: 0` and a `message` field |

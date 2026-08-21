# Google Custom Search

Search the web through Google's **Custom Search JSON API** and return the top matching links (title, URL, snippet). Designed as a small, MCP-compatible agent tool.

You need two credentials from Google Cloud / Programmable Search:

1. An API key with the Custom Search API enabled
2. A Programmable Search Engine ID (`cx`)

Keys are read from environment variables — never hardcode them.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | Search query keywords |
| `num` | `integer` | No | Number of results to return (1–10, default `5`) |
| `api_key` | `string` | No | Google API key (or set `GOOGLE_CSE_API_KEY`) |
| `cx` | `string` | No | Search Engine ID (or set `GOOGLE_CSE_ID`) |

## Installation & Setup

```bash
pip install -r requirements.txt

export GOOGLE_CSE_API_KEY="your-google-api-key"
export GOOGLE_CSE_ID="your-search-engine-id"
```

## Usage Example

```python
from tool import run_tool

response = run_tool(query="model context protocol", num=5)
if response["success"]:
    for item in response["data"]["results"]:
        print(f"- {item['title']}: {item['url']}")
else:
    print(response["error"])
```

### Example output

```json
{
  "success": true,
  "data": {
    "query": "model context protocol",
    "count": 5,
    "total_estimated": "12300",
    "results": [
      {
        "title": "Model Context Protocol",
        "url": "https://modelcontextprotocol.io/",
        "snippet": "The Model Context Protocol (MCP) is an open protocol..."
      }
    ]
  }
}
```

On missing credentials or API errors the tool returns `{"success": false, "error": "<reason>"}`.

# DuckDuckGo Search Tool

A zero-dependency search tool enabling AI agents to query DuckDuckGo for fast information retrieval.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | The query string to search for | - |
| `max_results` | `integer` | No | Maximum number of results | `5` |

## Usage

```python
from tool import search_duckduckgo

response = search_duckduckgo("Model Context Protocol", max_results=3)
if response["success"]:
    for item in response["results"]:
        print(f"- {item['title']}: {item['url']}")
```

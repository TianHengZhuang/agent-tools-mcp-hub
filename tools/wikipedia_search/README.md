# Wikipedia Knowledge Search Tool

Fetch structured knowledge summaries, topics, and canonical references from Wikipedia directly into AI agent prompts.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | Topic name to retrieve |
| `sentences` | `integer` | No | Number of summary sentences |

## Usage

```python
from tool import search_wikipedia

result = search_wikipedia("Artificial Intelligence")
if result["success"]:
    print(result["title"])
    print(result["extract"])
```

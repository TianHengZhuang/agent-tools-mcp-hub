# Example Tool

A template demonstrating how to build an Agent Tool integration.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `query` | `string` | Yes | The query string to process |

## Installation & Setup

```bash
pip install -r requirements.txt
```

## Usage Example

```python
from tool import run_tool

response = run_tool(query="test input")
print(response)
```

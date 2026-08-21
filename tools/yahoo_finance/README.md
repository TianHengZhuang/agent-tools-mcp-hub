# Yahoo Finance Stock Quote Tool

A tool to fetch current stock quotes and basic company info using the `yfinance` library. Fixes Issue #22.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `ticker` | `string` | Yes | The stock ticker symbol (e.g., 'AAPL', 'MSFT') |

## Installation & Setup

```bash
pip install -r requirements.txt
```

## Usage Example

```python
from tool import run_tool

response = run_tool(ticker="AAPL")
print(response)
```

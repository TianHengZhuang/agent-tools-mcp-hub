# Crypto Price Tracker Tool

A tool to fetch current cryptocurrency prices using the free CoinGecko API.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `coin_ids` | `string` | Yes | Comma-separated list of cryptocurrency ids (e.g., 'bitcoin,ethereum') |
| `currency` | `string` | No | The target currency (e.g., 'usd'). Defaults to 'usd'. |

## Installation & Setup

```bash
pip install -r requirements.txt
```

## Usage Example

```python
from tool import run_tool

response = run_tool(coin_ids="bitcoin,ethereum", currency="usd")
print(response)
```

# Crypto Price Checker Tool

A zero-auth tool allowing AI agents to query live market prices, 24-hour trends, and market capitalization for major cryptocurrencies.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `coin_id` | `string` | Yes | Token ID (e.g., `bitcoin`, `ethereum`, `solana`) | `bitcoin` |
| `currency` | `string` | No | Base currency (e.g., `usd`, `eur`, `inr`) | `usd` |

## Usage

```python
from tool import get_crypto_price

data = get_crypto_price(coin_id="bitcoin", currency="usd")
if data["success"]:
    print(f"Bitcoin Price: ${data['price']} (24h Change: {data['24h_change_pct']}%)")
```

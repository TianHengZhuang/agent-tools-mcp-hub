# Currency Exchange Rate Converter

A zero-auth converter that turns one fiat amount into another using public ECB rates from the Frankfurter API (`api.frankfurter.dev`).

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `from_currency` | `string` | Yes | ISO 4217 source currency code (e.g. `USD`) | - |
| `to_currency` | `string` | Yes | ISO 4217 target currency code (e.g. `INR`) | - |
| `amount` | `number` | No | Amount to convert | `1` |

## Usage

```python
from tool import convert_currency

result = convert_currency(from_currency="USD", to_currency="INR", amount=100)
if result["success"]:
    print(f"{result['amount']} {result['from']} = {result['converted']} {result['to']}")
```

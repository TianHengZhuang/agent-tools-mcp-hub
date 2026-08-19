"""
Currency Exchange Rate Converter using the Frankfurter API (ECB rates)
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Union

USER_AGENT = "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"


def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: Union[int, float] = 1,
) -> Dict[str, Any]:
    """
    Converts an amount from one currency to another using public ECB exchange rates.
    """
    if not from_currency or not str(from_currency).strip():
        return {"success": False, "error": "from_currency parameter is required."}
    if not to_currency or not str(to_currency).strip():
        return {"success": False, "error": "to_currency parameter is required."}

    source = str(from_currency).strip().upper()
    target = str(to_currency).strip().upper()

    if len(source) != 3 or not source.isalpha() or len(target) != 3 or not target.isalpha():
        return {
            "success": False,
            "error": "Currency codes must be 3-letter ISO values (e.g. USD, EUR, INR).",
        }

    try:
        value = float(amount)
    except (TypeError, ValueError):
        return {"success": False, "error": "amount must be a number."}

    if value <= 0:
        return {"success": False, "error": "amount must be greater than 0."}

    if source == target:
        return {
            "success": True,
            "from": source,
            "to": target,
            "amount": value,
            "rate": 1.0,
            "converted": value,
            "date": None,
        }

    params = urllib.parse.urlencode({"amount": value, "from": source, "to": target})
    url = f"{FRANKFURTER_URL}?{params}"
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        rates = data.get("rates") or {}
        if target not in rates:
            return {
                "success": False,
                "error": f"No conversion rate available from {source} to {target}.",
            }

        converted = rates[target]
        base_amount = data.get("amount", value)
        rate = converted / base_amount if base_amount else None

        return {
            "success": True,
            "from": data.get("base", source),
            "to": target,
            "amount": base_amount,
            "rate": rate,
            "converted": converted,
            "date": data.get("date"),
        }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {
                "success": False,
                "error": f"Unknown or unsupported currency pair: {source} to {target}.",
            }
        body = ""
        try:
            body = e.read().decode("utf-8")
            parsed = json.loads(body)
            message = parsed.get("message") or parsed.get("error") or body
        except Exception:
            message = body or e.reason
        return {
            "success": False,
            "error": f"Currency conversion failed ({e.code}): {message}",
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch exchange rate: {str(e)}"}


if __name__ == "__main__":
    result = convert_currency("USD", "INR", 100)
    print(json.dumps(result, indent=2))

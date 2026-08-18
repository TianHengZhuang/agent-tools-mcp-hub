"""
Crypto Price Checker Tool using CoinGecko Public API
"""
import urllib.request
import json
from typing import Dict, Any

def get_crypto_price(coin_id: str = "bitcoin", currency: str = "usd") -> Dict[str, Any]:
    """
    Fetches real-time price and 24h market stats for a given cryptocurrency.
    """
    if not coin_id:
        return {"success": False, "error": "coin_id parameter is required."}

    coin = coin_id.strip().lower()
    curr = currency.strip().lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies={curr}&include_24hr_change=true&include_market_cap=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (AgentToolsHub/1.0)",
        "Accept": "application/json"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if coin not in data:
            return {
                "success": False,
                "error": f"Cryptocurrency '{coin}' not found on CoinGecko."
            }

        coin_data = data[coin]
        return {
            "success": True,
            "coin": coin,
            "currency": curr,
            "price": coin_data.get(curr),
            "24h_change_pct": round(coin_data.get(f"{curr}_24h_change", 0.0), 2),
            "market_cap": coin_data.get(f"{curr}_market_cap")
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch crypto prices: {str(e)}"
        }

if __name__ == "__main__":
    res = get_crypto_price("ethereum", "usd")
    print("Test output:", json.dumps(res, indent=2))

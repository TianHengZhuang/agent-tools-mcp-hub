"""
Crypto Price Tracker Tool
"""
from typing import Dict, Any
import requests

def run_tool(coin_ids: str, currency: str = "usd", **kwargs: Any) -> Dict[str, Any]:
    """
    Executes the crypto price tracker logic using CoinGecko API.
    
    Args:
        coin_ids (str): Comma-separated list of cryptocurrency ids (e.g., 'bitcoin,ethereum').
        currency (str): The target currency to check the price in (e.g., 'usd', 'eur').
        
    Returns:
        Dict[str, Any]: Result dictionary containing status and output data.
    """
    if not coin_ids:
        return {
            "success": False,
            "error": "coin_ids parameter cannot be empty."
        }
    
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_ids,
        "vs_currencies": currency
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "data": data
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to fetch data from CoinGecko API: {str(e)}"
        }

if __name__ == "__main__":
    test_output = run_tool("bitcoin,ethereum")
    print("Test execution output:", test_output)

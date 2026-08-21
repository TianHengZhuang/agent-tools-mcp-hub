"""
Yahoo Finance Stock Quote Tool
"""
from typing import Dict, Any
import yfinance as yf

def run_tool(ticker: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Executes the Yahoo Finance tool logic to fetch stock quote.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL').
        
    Returns:
        Dict[str, Any]: Result dictionary containing status and stock data.
    """
    if not ticker:
        return {
            "success": False,
            "error": "ticker parameter cannot be empty."
        }
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract essential quote data
        data = {
            "symbol": ticker.upper(),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "currency": info.get("currency"),
            "day_high": info.get("dayHigh", info.get("regularMarketDayHigh")),
            "day_low": info.get("dayLow", info.get("regularMarketDayLow")),
            "volume": info.get("volume", info.get("regularMarketVolume")),
            "company_name": info.get("shortName", info.get("longName"))
        }
        
        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch data for ticker {ticker}: {str(e)}"
        }

if __name__ == "__main__":
    test_output = run_tool("AAPL")
    print("Test execution output:", test_output)

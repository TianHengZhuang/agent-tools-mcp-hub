"""
World Bank Global Economic Indicators Tool for AI Agents.
Fetches macroeconomic indicators using the zero-auth World Bank Open Data API.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

USER_AGENT = "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
BASE_API_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}?format=json&per_page={per_page}"

COMMON_INDICATORS = {
    "GDP_GROWTH": "NY.GDP.MKTP.KD.ZG",
    "INFLATION": "FP.CPI.TOTL.ZG",
    "POPULATION": "SP.POP.TOTL",
    "GDP_USD": "NY.GDP.MKTP.CD",
    "UNEMPLOYMENT": "SL.UEM.TOTL.ZS",
}


def _http_get_json(url: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        content = response.read().decode("utf-8")
        return json.loads(content)


def fetch_indicator(
    country: str = "US",
    indicator: str = "NY.GDP.MKTP.KD.ZG",
    years: int = 5,
) -> Dict[str, Any]:
    """
    Fetches macroeconomic indicators for a specific country from the World Bank API.
    """
    country_code = country.strip().upper()
    indicator_code = COMMON_INDICATORS.get(indicator.upper(), indicator.strip())

    url = BASE_API_URL.format(
        country=urllib.parse.quote(country_code),
        indicator=urllib.parse.quote(indicator_code),
        per_page=max(1, min(years, 50)),
    )

    try:
        data = _http_get_json(url)
        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            return {
                "success": False,
                "country": country_code,
                "indicator": indicator_code,
                "error": "No data returned for specified country and indicator.",
            }

        records = data[1]
        results = []
        for item in records:
            results.append({
                "year": item.get("date"),
                "value": item.get("value"),
                "indicator_name": item.get("indicator", {}).get("value"),
                "country_name": item.get("country", {}).get("value"),
            })

        return {
            "success": True,
            "country": country_code,
            "indicator": indicator_code,
            "count": len(results),
            "data": results,
        }
    except Exception as e:
        return {
            "success": False,
            "country": country_code,
            "indicator": indicator_code,
            "error": str(e),
        }


def run_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    country = params.get("country", "US")
    indicator = params.get("indicator", "NY.GDP.MKTP.KD.ZG")
    years = int(params.get("years", 5))
    return fetch_indicator(country=country, indicator=indicator, years=years)


if __name__ == "__main__":
    result = run_tool({"country": "US", "indicator": "NY.GDP.MKTP.KD.ZG", "years": 3})
    print(json.dumps(result, indent=2))

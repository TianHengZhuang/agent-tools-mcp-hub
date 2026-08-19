"""
Open-Meteo Weather Tool for AI Agents
"""
import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

USER_AGENT = "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def _describe_weather(code: Any) -> str:
    try:
        return WMO_WEATHER_CODES.get(int(code), f"Unknown weather code {code}")
    except (TypeError, ValueError):
        return "Unknown"


def _http_get_json(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def get_weather(city: str, forecast_days: int = 7) -> Dict[str, Any]:
    """
    Fetches current weather and a daily forecast for a city using Open-Meteo.
    """
    if not city or not str(city).strip():
        return {"success": False, "error": "city parameter is required."}

    try:
        days = int(forecast_days)
    except (TypeError, ValueError):
        return {"success": False, "error": "forecast_days must be an integer between 1 and 16."}

    if days < 1 or days > 16:
        return {"success": False, "error": "forecast_days must be an integer between 1 and 16."}

    query = str(city).strip()
    geocode_params = urllib.parse.urlencode({"name": query, "count": 1, "language": "en", "format": "json"})

    try:
        geo = _http_get_json(f"{GEOCODE_URL}?{geocode_params}")
        matches: List[Dict[str, Any]] = geo.get("results") or []
        if not matches:
            return {"success": False, "error": f"Location '{query}' was not found."}

        place = matches[0]
        latitude = place.get("latitude")
        longitude = place.get("longitude")
        if latitude is None or longitude is None:
            return {"success": False, "error": f"Location '{query}' is missing coordinates."}

        forecast_params = urllib.parse.urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "forecast_days": days,
                "timezone": "auto",
            }
        )
        forecast = _http_get_json(f"{FORECAST_URL}?{forecast_params}")

        current = forecast.get("current") or {}
        daily = forecast.get("daily") or {}
        current_code = current.get("weather_code")

        forecast_entries = []
        dates = daily.get("time") or []
        for idx, date in enumerate(dates):
            day_code = (daily.get("weather_code") or [None])[idx] if idx < len(daily.get("weather_code") or []) else None
            max_temps = daily.get("temperature_2m_max") or []
            min_temps = daily.get("temperature_2m_min") or []
            precip = daily.get("precipitation_sum") or []
            forecast_entries.append(
                {
                    "date": date,
                    "weather_code": day_code,
                    "conditions": _describe_weather(day_code),
                    "temp_max_c": max_temps[idx] if idx < len(max_temps) else None,
                    "temp_min_c": min_temps[idx] if idx < len(min_temps) else None,
                    "precipitation_mm": precip[idx] if idx < len(precip) else None,
                }
            )

        location_parts = [place.get("name"), place.get("admin1"), place.get("country")]
        location_label = ", ".join(part for part in location_parts if part)

        return {
            "success": True,
            "location": {
                "name": location_label or query,
                "city": place.get("name"),
                "country": place.get("country"),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": forecast.get("timezone") or place.get("timezone"),
            },
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "weather_code": current_code,
                "conditions": _describe_weather(current_code),
                "time": current.get("time"),
            },
            "forecast": forecast_entries,
            "forecast_days": len(forecast_entries),
        }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch weather: {str(e)}"}


if __name__ == "__main__":
    result = get_weather("London", forecast_days=7)
    print(json.dumps(result, indent=2))

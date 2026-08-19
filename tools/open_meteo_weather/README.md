# Open-Meteo Weather Tool

A zero-auth weather tool that returns current conditions and a daily forecast for any city using the public Open-Meteo API.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `city` | `string` | Yes | City or place name to look up | - |
| `forecast_days` | `integer` | No | Number of forecast days to return (1-16) | `7` |

## Usage

```python
from tool import get_weather

result = get_weather(city="London", forecast_days=7)
if result["success"]:
    current = result["current"]
    print(f"{result['location']['name']}: {current['temperature_c']}°C, {current['conditions']}")
    for day in result["forecast"]:
        print(f"- {day['date']}: {day['temp_min_c']}–{day['temp_max_c']}°C, {day['conditions']}")
```

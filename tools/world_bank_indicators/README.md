# World Bank Global Economic Indicators Tool

Queries the World Bank Open Data API to fetch macroeconomic indicators such as GDP growth, inflation, population, and unemployment across countries.

## Parameters

* `country` (string, default: `"US"`): ISO2 or ISO3 country code (e.g. `US`, `IN`, `GB`, `DE`).
* `indicator` (string, default: `"NY.GDP.MKTP.KD.ZG"`): World Bank indicator code or alias (`GDP_GROWTH`, `INFLATION`, `POPULATION`).
* `years` (integer, default: `5`): Number of recent annual data points to fetch.

## Example Output

```json
{
  "success": true,
  "country": "US",
  "indicator": "NY.GDP.MKTP.KD.ZG",
  "count": 3,
  "data": [
    {
      "year": "2024",
      "value": 2.8,
      "indicator_name": "GDP growth (annual %)",
      "country_name": "United States"
    }
  ]
}
```

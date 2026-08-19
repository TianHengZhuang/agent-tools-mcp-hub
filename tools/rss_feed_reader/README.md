# RSS / Atom Feed Reader

A zero-auth tool that fetches any RSS or Atom feed URL and returns the latest articles for AI agents.

## Parameters

| Parameter | Type | Required | Description | Default |
| :--- | :--- | :--- | :--- | :--- |
| `feed_url` | `string` | Yes | HTTP or HTTPS URL of the RSS or Atom feed | - |
| `max_results` | `integer` | No | Maximum number of articles to return (1-25) | `5` |

## Usage

```python
from tool import read_feed

result = read_feed(feed_url="https://hnrss.org/frontpage", max_results=5)
if result["success"]:
    for article in result["articles"]:
        print(f"{article['title']}: {article['url']}")
```

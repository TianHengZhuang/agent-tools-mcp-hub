# HackerNews Profile & Karma Checker

Fetches HackerNews user profiles with karma, creation date, and submission count. Also retrieves top stories with scores and comment counts.

## Features

- **User Profile Lookup**: Get karma, join date, about info, and submission count
- **Top Stories**: Fetch current top stories with scores and comment counts
- **No API Key Required**: Uses HackerNews's public Firebase API

## Usage

```python
from tool import get_user_profile, get_top_stories

# Get user profile
profile = get_user_profile("pg")
print(profile)
# {
#   "success": true,
#   "username": "pg",
#   "karma": 157836,
#   "created": "2006-10-09",
#   "about": "Bug Fixer...",
#   "submitted_count": 1234,
#   "profile_url": "https://news.ycombinator.com/user?id=pg"
# }

# Get top stories
stories = get_top_stories(5)
print(stories)
```

## Parameters

### get_user_profile(username)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | HackerNews username |

### get_top_stories(limit)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Number of stories (default: 10) |

## API Reference

Uses the official [HackerNews API](https://github.com/HackerNews/API):
- User: `https://hacker-news.firebaseio.com/v0/user/{username}.json`
- Top stories: `https://hacker-news.firebaseio.com/v0/topstories.json`
- Item: `https://hacker-news.firebaseio.com/v0/item/{id}.json`

## License

MIT

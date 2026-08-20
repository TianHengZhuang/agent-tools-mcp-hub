"""
HackerNews User Profile & Karma Checker Tool
"""
import urllib.request
import json
from typing import Dict, Any


def get_user_profile(username: str) -> Dict[str, Any]:
    """
    Fetches HackerNews user profile including karma, created date, and about info.
    """
    if not username or not username.strip():
        return {"success": False, "error": "Username is required."}

    url = f"https://hacker-news.firebaseio.com/v0/user/{username.strip()}.json"

    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "AgentToolsHub/1.0")
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data is None:
            return {"success": False, "error": f"HackerNews user '{username}' not found."}

        # Convert Unix timestamp to readable date
        created_timestamp = data.get("created", 0)
        created_date = ""
        if created_timestamp:
            from datetime import datetime
            created_date = datetime.fromtimestamp(created_timestamp).strftime("%Y-%m-%d")

        return {
            "success": True,
            "username": data.get("id", username),
            "karma": data.get("karma", 0),
            "created": created_date,
            "about": data.get("about", ""),
            "submitted_count": len(data.get("submitted", [])),
            "profile_url": f"https://news.ycombinator.com/user?id={username.strip()}"
        }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"success": False, "error": f"HackerNews user '{username}' not found."}
        return {"success": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"HackerNews query error: {str(e)}"}


def get_top_stories(limit: int = 10) -> Dict[str, Any]:
    """
    Fetches top HackerNews stories.
    """
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "AgentToolsHub/1.0")
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read().decode("utf-8"))

        stories = []
        for story_id in story_ids[:limit]:
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(story_url)
            req.add_header("User-Agent", "AgentToolsHub/1.0")
            with urllib.request.urlopen(req, timeout=5) as response:
                story = json.loads(response.read().decode("utf-8"))
                if story:
                    stories.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", ""),
                        "score": story.get("score", 0),
                        "by": story.get("by", ""),
                        "comments": story.get("descendants", 0),
                        "hn_url": f"https://news.ycombinator.com/item?id={story_id}"
                    })

        return {
            "success": True,
            "stories": stories,
            "count": len(stories)
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to fetch top stories: {str(e)}"}


if __name__ == "__main__":
    # Test user profile
    result = get_user_profile("pg")
    print("User Profile:")
    print(json.dumps(result, indent=2))

    print("\nTop 3 Stories:")
    result = get_top_stories(3)
    print(json.dumps(result, indent=2))

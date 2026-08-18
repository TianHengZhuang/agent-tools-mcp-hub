"""
Wikipedia Knowledge Extractor Tool
"""
import urllib.parse
import urllib.request
import json
from typing import Dict, Any

def search_wikipedia(query: str, sentences: int = 3) -> Dict[str, Any]:
    """
    Queries Wikipedia REST API for page extracts and summaries.
    """
    if not query or not query.strip():
        return {"success": False, "error": "Query string is required."}

    encoded_title = urllib.parse.quote(query.strip().replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

    headers = {
        "User-Agent": "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub; contact@example.com)"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))

        if data.get("type") == "disambiguation":
            return {
                "success": True,
                "title": data.get("title"),
                "is_disambiguation": True,
                "extract": data.get("extract"),
                "description": "Topic has multiple meanings.",
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
            }

        return {
            "success": True,
            "title": data.get("title"),
            "extract": data.get("extract"),
            "description": data.get("description", ""),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
        }
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"success": False, "error": f"Wikipedia article for '{query}' not found."}
        return {"success": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except Exception as e:
        return {"success": False, "error": f"Wikipedia query error: {str(e)}"}

if __name__ == "__main__":
    res = search_wikipedia("Artificial Intelligence")
    print(json.dumps(res, indent=2))

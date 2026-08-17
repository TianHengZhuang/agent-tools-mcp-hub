"""
DuckDuckGo Web Search Tool for AI Agents
"""
import urllib.parse
import urllib.request
import json
import re
from typing import Dict, Any, List

def search_duckduckgo(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search DuckDuckGo using the instant answer / html API and return formatted results.
    """
    if not query or not query.strip():
        return {"success": False, "error": "Search query cannot be empty."}

    encoded_query = urllib.parse.quote_plus(query.strip())
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AgentToolsHub/1.0)"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        results: List[Dict[str, str]] = []
        
        # Abstract
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", query),
                "snippet": data.get("Abstract"),
                "url": data.get("AbstractURL", "")
            })
            
        # Related topics
        for topic in data.get("RelatedTopics", []):
            if len(results) >= max_results:
                break
            if "Text" in topic and "FirstURL" in topic:
                results.append({
                    "title": topic.get("Text", "").split(" - ")[0],
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute search: {str(e)}"
        }

if __name__ == "__main__":
    res = search_duckduckgo("Model Context Protocol Specification")
    print(json.dumps(res, indent=2))

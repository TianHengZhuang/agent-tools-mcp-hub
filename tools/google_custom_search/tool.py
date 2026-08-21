"""
Google Custom Search JSON API tool for AI agents and MCP Hub.

Searches the web via a Programmable Search Engine and returns the top results
(title, URL, snippet). Requires a Google API key and a Search Engine ID (cx).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

API_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
MAX_RESULTS = 10  # Google Custom Search allows 1-10 items per request.


def _env(name: str, *aliases: str) -> str:
    for key in (name, *aliases):
        value = os.getenv(key)
        if value and value.strip():
            return value.strip()
    return ""


def search_google(
    query: str,
    num: int = 5,
    api_key: Optional[str] = None,
    cx: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Query Google's Custom Search JSON API and return the top matching links.

    Args:
        query: Search query string.
        num: Number of results to return (1-10, default 5).
        api_key: Google Cloud API key. Falls back to GOOGLE_CSE_API_KEY
            or GOOGLE_API_KEY.
        cx: Programmable Search Engine ID. Falls back to GOOGLE_CSE_ID
            or GOOGLE_SEARCH_ENGINE_ID.

    Returns:
        Dict with success/error status and a list of {title, url, snippet}.
    """
    query = (query or kwargs.get("q") or "").strip()
    if not query:
        return {"success": False, "error": "Query parameter cannot be empty."}

    token = (api_key or _env("GOOGLE_CSE_API_KEY", "GOOGLE_API_KEY")).strip()
    engine_id = (cx or _env("GOOGLE_CSE_ID", "GOOGLE_SEARCH_ENGINE_ID")).strip()

    if not token:
        return {
            "success": False,
            "error": (
                "Google API key is required. Pass api_key or set the "
                "GOOGLE_CSE_API_KEY environment variable."
            ),
        }
    if not engine_id:
        return {
            "success": False,
            "error": (
                "Programmable Search Engine ID (cx) is required. Pass cx or set "
                "the GOOGLE_CSE_ID environment variable."
            ),
        }

    try:
        num = int(num)
    except (TypeError, ValueError):
        return {"success": False, "error": "Parameter 'num' must be an integer between 1 and 10."}
    num = max(1, min(num, MAX_RESULTS))

    params = {"key": token, "cx": engine_id, "q": query, "num": num}
    url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)",
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        message = _parse_google_error(exc.code, body)
        return {"success": False, "error": message, "status_code": exc.code}
    except urllib.error.URLError as exc:
        return {"success": False, "error": f"Network connection error: {exc.reason}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Google Custom Search returned a non-JSON response."}
    except Exception as exc:
        return {"success": False, "error": f"Unexpected error while querying Google Custom Search: {exc}"}

    results: List[Dict[str, str]] = []
    for item in payload.get("items") or []:
        results.append(
            {
                "title": item.get("title") or "",
                "url": item.get("link") or "",
                "snippet": item.get("snippet") or "",
            }
        )

    data: Dict[str, Any] = {
        "query": query,
        "count": len(results),
        "total_estimated": (payload.get("searchInformation") or {}).get("totalResults"),
        "results": results,
    }
    if not results:
        data["message"] = "No search results found for this query."

    return {"success": True, "data": data}


def _parse_google_error(status: int, body: str) -> str:
    try:
        err = json.loads(body).get("error") or {}
        message = err.get("message") or ""
        if message:
            return f"Google Custom Search API error {status}: {message}"
    except Exception:
        pass
    if status == 403:
        return "Google Custom Search API error 403: invalid API key, disabled API, or daily quota exceeded."
    if status == 429:
        return "Google Custom Search API error 429: rate limit exceeded."
    return f"Google Custom Search API error {status}."


def run_tool(query: str = "", **kwargs: Any) -> Dict[str, Any]:
    """Standard agent dispatcher entrypoint used by this hub."""
    return search_google(
        query=kwargs.get("query") or query,
        num=kwargs.get("num", 5),
        api_key=kwargs.get("api_key"),
        cx=kwargs.get("cx"),
    )


if __name__ == "__main__":
    print("Google Custom Search tool loaded.")
    print("Without GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID the tool fails gracefully:")
    print(json.dumps(run_tool("model context protocol"), indent=2))

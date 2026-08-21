"""
Brave Search API Web Connector for AI Agents and MCP Hub.
Queries the Brave Search REST API for privacy-first web results and optional AI summaries.
"""
import os
import re
import gzip
import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

API_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
SUMMARIZER_ENDPOINT = "https://api.search.brave.com/res/v1/summarizer/search"

MAX_COUNT = 20
VALID_SAFESEARCH = ("off", "moderate", "strict")

_TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: Optional[str]) -> str:
    """Brave highlights matched terms with <strong> tags; strip them for agent consumption."""
    if not text:
        return ""
    return urllib.parse.unquote(_TAG_RE.sub("", text)).strip()


def _read_body(resp: Any) -> str:
    """Reads a response body, transparently decompressing gzip when present."""
    raw = resp.read()
    if resp.headers.get("Content-Encoding", "").lower() == "gzip":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def _parse_api_error(status: int, body: str) -> str:
    """Turns a Brave ErrorResponse payload into a readable message."""
    try:
        payload = json.loads(body)
        err = payload.get("error", {})
        detail = err.get("detail") or err.get("message")
        code = err.get("code")
        if detail and code:
            return f"Brave Search API error {status} ({code}): {detail}"
        if detail:
            return f"Brave Search API error {status}: {detail}"
    except Exception:
        pass
    return f"Brave Search API error {status}."


def _extract_results(web_block: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    for item in web_block.get("results", []):
        profile = item.get("profile") or {}
        results.append({
            "title": _clean(item.get("title")),
            "url": item.get("url"),
            "description": _clean(item.get("description")),
            "source": profile.get("name") or item.get("meta_url", {}).get("hostname"),
            "age": item.get("age") or item.get("page_age"),
            "extra_snippets": [_clean(s) for s in item.get("extra_snippets", [])],
        })
    return results


def search_brave(
    query: str,
    count: int = 5,
    country: str = "US",
    search_lang: str = "en",
    safesearch: str = "moderate",
    freshness: Optional[str] = None,
    summary: bool = False,
    api_key: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Runs a web search against the Brave Search API.

    Args:
        query (str): The search query.
        count (int): Number of results to return (1-20, default 5).
        country (str): Two-letter country code for result localisation (default 'US').
        search_lang (str): Language code for the results (default 'en').
        safesearch (str): Adult content filter - 'off', 'moderate' or 'strict' (default 'moderate').
        freshness (str, optional): Restrict results by age - 'pd', 'pw', 'pm', 'py'
            or a range like '2024-01-01to2024-06-30'.
        summary (bool): Request an AI summary key alongside the results. Requires a
            Brave subscription plan that includes the Summarizer.
        api_key (str, optional): Brave Search subscription token. Falls back to the
            BRAVE_SEARCH_API_KEY (or BRAVE_API_KEY) environment variable.

    Returns:
        Dict[str, Any]: Result dictionary containing success status, results, or an error message.
    """
    token = api_key or os.getenv("BRAVE_SEARCH_API_KEY") or os.getenv("BRAVE_API_KEY")

    if not token:
        return {
            "success": False,
            "error": "Brave Search API key is required. Pass api_key or set the BRAVE_SEARCH_API_KEY environment variable."
        }

    if not query or not str(query).strip():
        return {
            "success": False,
            "error": "Query parameter cannot be empty."
        }

    try:
        count = int(count)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Parameter 'count' must be an integer between 1 and 20."
        }
    count = max(1, min(count, MAX_COUNT))

    safesearch = str(safesearch).lower()
    if safesearch not in VALID_SAFESEARCH:
        return {
            "success": False,
            "error": f"Parameter 'safesearch' must be one of {', '.join(VALID_SAFESEARCH)}."
        }

    params = {
        "q": str(query).strip(),
        "count": count,
        "country": country,
        "search_lang": search_lang,
        "safesearch": safesearch,
    }
    if freshness:
        params["freshness"] = freshness
    if summary:
        params["summary"] = 1

    url = f"{API_ENDPOINT}?{urllib.parse.urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": token,
        "User-Agent": "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(_read_body(resp))

    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = _read_body(e)
        except Exception:
            pass
        if e.code == 401 or e.code == 422:
            return {
                "success": False,
                "error": _parse_api_error(e.code, body) or "Invalid or missing Brave Search subscription token.",
                "status_code": e.code
            }
        if e.code == 429:
            return {
                "success": False,
                "error": "Brave Search rate limit exceeded. Slow down requests or upgrade your plan.",
                "status_code": 429
            }
        return {
            "success": False,
            "error": _parse_api_error(e.code, body),
            "status_code": e.code
        }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Network connection error: {str(e.reason)}"
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Brave Search returned a response that could not be parsed as JSON."
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error while querying Brave Search: {str(e)}"
        }

    results = _extract_results(data.get("web") or {})

    payload: Dict[str, Any] = {
        "success": True,
        "data": {
            "query": data.get("query", {}).get("original", params["q"]),
            "count": len(results),
            "results": results
        }
    }

    # Present only when the account's plan includes the Summarizer and summary=True was passed.
    summarizer_key = (data.get("summarizer") or {}).get("key")
    if summarizer_key:
        payload["data"]["summarizer_key"] = summarizer_key
        payload["data"]["summarizer_endpoint"] = SUMMARIZER_ENDPOINT

    if not results:
        payload["data"]["message"] = "No web results found for this query."

    return payload


def run_tool(query: str = "", **kwargs: Any) -> Dict[str, Any]:
    """
    Standard agent dispatcher entrypoint.
    Accepts 'query' plus any of the optional Brave Search parameters.
    """
    return search_brave(
        query=kwargs.get("query") or query,
        count=kwargs.get("count", 5),
        country=kwargs.get("country", "US"),
        search_lang=kwargs.get("search_lang", "en"),
        safesearch=kwargs.get("safesearch", "moderate"),
        freshness=kwargs.get("freshness"),
        summary=kwargs.get("summary", False),
        api_key=kwargs.get("api_key"),
    )


if __name__ == "__main__":
    print("Brave Search Web Connector loaded.")
    print("Set BRAVE_SEARCH_API_KEY to run a live query; without it the tool fails gracefully:")
    print(json.dumps(run_tool("model context protocol", count=3), indent=2))

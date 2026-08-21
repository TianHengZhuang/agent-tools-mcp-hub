"""
GitHub Repository Info Tool

Fetches public metadata for any GitHub repository (stars, forks, primary
language, open issues, license, topics and description) using the public
GitHub REST API. No API key is required; an optional GITHUB_TOKEN raises
the rate limit.
"""
from typing import Dict, Any
import os
import requests

GITHUB_API = "https://api.github.com/repos/{owner}/{repo}"


def run_tool(query: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Fetch public information about a GitHub repository.

    Args:
        query (str): Repository in "owner/repo" format
            (e.g. "tarunjandra/agent-tools-mcp-hub").

    Returns:
        Dict[str, Any]: {"success": True, "data": {...}} on success, or
            {"success": False, "error": "..."} on failure.
    """
    if not query or "/" not in query:
        return {
            "success": False,
            "error": "Query must be in 'owner/repo' format, e.g. 'openai/openai-python'.",
        }

    owner, _, repo = query.strip().partition("/")
    owner, repo = owner.strip(), repo.strip().rstrip("/")
    if not owner or not repo:
        return {"success": False, "error": "Both owner and repo are required, e.g. 'owner/repo'."}

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "agent-tools-mcp-hub"}
    token = os.getenv("GITHUB_TOKEN")  # optional; never hardcode secrets
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(
            GITHUB_API.format(owner=owner, repo=repo), headers=headers, timeout=15
        )
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code == 404:
        return {"success": False, "error": f"Repository '{owner}/{repo}' not found."}
    if resp.status_code == 403 and "rate limit" in resp.text.lower():
        return {
            "success": False,
            "error": "GitHub API rate limit reached. Set GITHUB_TOKEN to raise the limit.",
        }
    if resp.status_code != 200:
        return {"success": False, "error": f"GitHub API returned status {resp.status_code}."}

    data = resp.json()
    return {
        "success": True,
        "data": {
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "license": (data.get("license") or {}).get("spdx_id"),
            "topics": data.get("topics", []),
            "homepage": data.get("homepage"),
            "url": data.get("html_url"),
            "last_pushed": data.get("pushed_at"),
        },
    }


if __name__ == "__main__":
    print(run_tool("tarunjandra/agent-tools-mcp-hub"))

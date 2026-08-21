"""
GitHub Issue & PR Manager Tool

Supports:
- Listing repository issues
- Listing repository pull requests
- Creating a new issue
- Creating a comment on an issue or PR
"""
from typing import Dict, Any, Optional
import os
import requests


GITHUB_API_BASE = "https://api.github.com"
USER_AGENT = "agent-tools-mcp-hub/github-issue-pr-manager"


def _get_repo_parts(repo: str) -> Optional[tuple[str, str]]:
    if not repo or "/" not in repo:
        return None
    owner, _, name = repo.strip().partition("/")
    owner = owner.strip()
    name = name.strip().rstrip("/")
    if not owner or not name:
        return None
    return owner, name


def _headers(token: Optional[str]) -> Dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _format_error(resp: requests.Response) -> str:
    try:
        payload = resp.json()
        message = payload.get("message")
        if message:
            docs_url = payload.get("documentation_url")
            if docs_url:
                return f"GitHub API error ({resp.status_code}): {message}. See: {docs_url}"
            return f"GitHub API error ({resp.status_code}): {message}"
    except ValueError:
        pass
    if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
        reset_ts = resp.headers.get("X-RateLimit-Reset", "unknown")
        return f"GitHub API rate limit exceeded. Rate limit resets at unix timestamp: {reset_ts}."
    return f"GitHub API returned status {resp.status_code}."


def _coerce_int(value: Any, default: int, minimum: int = 1) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, parsed)


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _list_issues(
    repo: str,
    state: str = "open",
    per_page: int = 10,
    page: int = 1,
    include_pull_requests: bool = False,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    repo_parts = _get_repo_parts(repo)
    if not repo_parts:
        return {"success": False, "error": "Parameter 'repo' must be in 'owner/repo' format."}

    owner, name = repo_parts
    url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/issues"
    params = {"state": state, "per_page": max(1, min(per_page, 100)), "page": max(1, page)}

    try:
        resp = requests.get(url, headers=_headers(token), params=params, timeout=20)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code != 200:
        return {"success": False, "error": _format_error(resp)}

    raw_items = resp.json()
    issues = []
    for item in raw_items:
        is_pr = "pull_request" in item
        if is_pr and not include_pull_requests:
            continue
        issues.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "comments": item.get("comments"),
                "is_pull_request": is_pr,
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
            }
        )

    return {
        "success": True,
        "data": {
            "repo": f"{owner}/{name}",
            "state": state,
            "count": len(issues),
            "issues": issues,
        },
    }


def _list_pull_requests(
    repo: str,
    state: str = "open",
    per_page: int = 10,
    page: int = 1,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    repo_parts = _get_repo_parts(repo)
    if not repo_parts:
        return {"success": False, "error": "Parameter 'repo' must be in 'owner/repo' format."}

    owner, name = repo_parts
    url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/pulls"
    params = {"state": state, "per_page": max(1, min(per_page, 100)), "page": max(1, page)}

    try:
        resp = requests.get(url, headers=_headers(token), params=params, timeout=20)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code != 200:
        return {"success": False, "error": _format_error(resp)}

    pulls = []
    for item in resp.json():
        pulls.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "state": item.get("state"),
                "author": (item.get("user") or {}).get("login"),
                "draft": item.get("draft"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
            }
        )

    return {
        "success": True,
        "data": {
            "repo": f"{owner}/{name}",
            "state": state,
            "count": len(pulls),
            "pull_requests": pulls,
        },
    }


def _create_issue(
    repo: str,
    title: str,
    body: str = "",
    labels: Optional[list[str]] = None,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    repo_parts = _get_repo_parts(repo)
    if not repo_parts:
        return {"success": False, "error": "Parameter 'repo' must be in 'owner/repo' format."}
    if not title or not title.strip():
        return {"success": False, "error": "Parameter 'title' is required for create_issue action."}
    if not token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN is required for create_issue action.",
        }

    owner, name = repo_parts
    url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/issues"
    payload: Dict[str, Any] = {"title": title.strip(), "body": body or ""}
    if labels:
        payload["labels"] = labels

    try:
        resp = requests.post(url, headers=_headers(token), json=payload, timeout=20)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code not in (200, 201):
        return {"success": False, "error": _format_error(resp)}

    item = resp.json()
    return {
        "success": True,
        "data": {
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "labels": [(label or {}).get("name") for label in item.get("labels", [])],
            "url": item.get("html_url"),
        },
    }


def _create_issue_comment(
    repo: str,
    issue_number: int,
    comment_body: str,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    repo_parts = _get_repo_parts(repo)
    if not repo_parts:
        return {"success": False, "error": "Parameter 'repo' must be in 'owner/repo' format."}
    if not issue_number:
        return {"success": False, "error": "Parameter 'issue_number' is required for create_issue_comment action."}
    if not comment_body or not comment_body.strip():
        return {"success": False, "error": "Parameter 'comment_body' is required for create_issue_comment action."}
    if not token:
        return {
            "success": False,
            "error": "GITHUB_TOKEN is required for create_issue_comment action.",
        }

    owner, name = repo_parts
    url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/issues/{issue_number}/comments"
    payload = {"body": comment_body.strip()}

    try:
        resp = requests.post(url, headers=_headers(token), json=payload, timeout=20)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code not in (200, 201):
        return {"success": False, "error": _format_error(resp)}

    comment = resp.json()
    return {
        "success": True,
        "data": {
            "id": comment.get("id"),
            "issue_url": comment.get("issue_url"),
            "comment_url": comment.get("html_url"),
            "created_at": comment.get("created_at"),
        },
    }


def _get_issue(
    repo: str,
    issue_number: int,
    token: Optional[str] = None,
) -> Dict[str, Any]:
    repo_parts = _get_repo_parts(repo)
    if not repo_parts:
        return {"success": False, "error": "Parameter 'repo' must be in 'owner/repo' format."}
    if not issue_number:
        return {"success": False, "error": "Parameter 'issue_number' is required for get_issue action."}

    owner, name = repo_parts
    url = f"{GITHUB_API_BASE}/repos/{owner}/{name}/issues/{issue_number}"

    try:
        resp = requests.get(url, headers=_headers(token), timeout=20)
    except requests.RequestException as exc:
        return {"success": False, "error": f"Network error contacting GitHub: {exc}"}

    if resp.status_code != 200:
        return {"success": False, "error": _format_error(resp)}

    item = resp.json()
    return {
        "success": True,
        "data": {
            "repo": f"{owner}/{name}",
            "number": item.get("number"),
            "title": item.get("title"),
            "state": item.get("state"),
            "author": (item.get("user") or {}).get("login"),
            "comments": item.get("comments"),
            "labels": [(label or {}).get("name") for label in item.get("labels", [])],
            "is_pull_request": "pull_request" in item,
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "url": item.get("html_url"),
        },
    }


def run_tool(query: str = "", **kwargs: Any) -> Dict[str, Any]:
    """
    Dispatches GitHub actions.

    Actions:
      - list_issues
      - list_pull_requests
      - get_issue
      - create_issue
      - create_issue_comment
    """
    action = (kwargs.get("action") or "list_issues").strip()
    repo = kwargs.get("repo") or query
    state = kwargs.get("state", "open")
    per_page = _coerce_int(kwargs.get("per_page", 10), default=10, minimum=1)
    page = _coerce_int(kwargs.get("page", 1), default=1, minimum=1)
    include_pull_requests = _coerce_bool(kwargs.get("include_pull_requests", False), default=False)
    title = kwargs.get("title", "")
    body = kwargs.get("body", "")
    labels_raw = kwargs.get("labels")
    issue_number = kwargs.get("issue_number")
    comment_body = kwargs.get("comment_body", "")
    token = kwargs.get("github_token") or os.getenv("GITHUB_TOKEN")
    labels: list[str] = []

    if isinstance(labels_raw, list):
        labels = [str(label).strip() for label in labels_raw if str(label).strip()]
    elif isinstance(labels_raw, str) and labels_raw.strip():
        labels = [segment.strip() for segment in labels_raw.split(",") if segment.strip()]

    if state not in {"open", "closed", "all"}:
        return {"success": False, "error": "Parameter 'state' must be one of: open, closed, all."}

    if action == "list_issues":
        return _list_issues(
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
            include_pull_requests=include_pull_requests,
            token=token,
        )
    if action == "list_pull_requests":
        return _list_pull_requests(
            repo=repo,
            state=state,
            per_page=per_page,
            page=page,
            token=token,
        )
    if action == "get_issue":
        try:
            issue_number_int = int(issue_number)
        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "Parameter 'issue_number' must be a valid integer for get_issue action.",
            }
        return _get_issue(repo=repo, issue_number=issue_number_int, token=token)
    if action == "create_issue":
        return _create_issue(repo=repo, title=title, body=body, labels=labels, token=token)
    if action == "create_issue_comment":
        try:
            issue_number_int = int(issue_number)
        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "Parameter 'issue_number' must be a valid integer for create_issue_comment action.",
            }
        return _create_issue_comment(
            repo=repo,
            issue_number=issue_number_int,
            comment_body=comment_body,
            token=token,
        )

    return {
        "success": False,
        "error": "Unsupported action. Use one of: list_issues, list_pull_requests, get_issue, create_issue, create_issue_comment.",
    }


if __name__ == "__main__":
    example = run_tool(
        action="list_issues",
        repo="tarunjandra/agent-tools-mcp-hub",
        per_page=3,
    )
    print(example)

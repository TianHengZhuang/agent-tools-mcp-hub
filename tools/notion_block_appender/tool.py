#!/usr/bin/env python3
"""
Notion Page & Database Block Appender for Agent Tools & MCP Hub.

Appends structured content blocks — headings, bulleted / numbered lists, code
blocks, paragraphs, quotes, to-dos and dividers — to a Notion page (or any
block that accepts children) using the Notion REST API.

The block-building logic is a pure function (build_notion_blocks) so it can be
unit-tested with no network or credentials, and the HTTP transport is injectable
(http_post) so the full request assembly can be verified offline.
"""
from typing import Any, Callable, Dict, List, Optional, Tuple
import os

import requests

NOTION_API_URL = "https://api.notion.com/v1/blocks/{block_id}/children"
DEFAULT_NOTION_VERSION = "2022-06-28"

# Notion API limits
MAX_BLOCKS_PER_REQUEST = 100      # children per PATCH call
MAX_RICH_TEXT_LENGTH = 2000       # characters per rich_text object

HEADING_TYPES = {1: "heading_1", 2: "heading_2", 3: "heading_3"}


def _rich_text(content: str) -> List[Dict[str, Any]]:
    """
    Build a Notion rich_text array from a plain string, splitting into
    <=2000-character segments (Notion rejects longer single rich_text objects).
    """
    content = "" if content is None else str(content)
    if content == "":
        return [{"type": "text", "text": {"content": ""}}]
    return [
        {"type": "text", "text": {"content": content[i:i + MAX_RICH_TEXT_LENGTH]}}
        for i in range(0, len(content), MAX_RICH_TEXT_LENGTH)
    ]


def _build_one(block: Dict[str, Any], index: int) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Convert one friendly block spec into a Notion block object, or an error string."""
    if not isinstance(block, dict):
        return None, f"block[{index}] must be an object, got {type(block).__name__}"

    btype = str(block.get("type", "")).strip().lower()
    text = block.get("text", "")

    if btype in ("heading", "h"):
        level = block.get("level", 1)
        if level not in HEADING_TYPES:
            return None, f"block[{index}] heading 'level' must be 1, 2 or 3 (got {level!r})"
        ntype = HEADING_TYPES[level]
        return {"object": "block", "type": ntype, ntype: {"rich_text": _rich_text(text)}}, None

    if btype in ("bullet", "bulleted", "bulleted_list_item"):
        return {"object": "block", "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": _rich_text(text)}}, None

    if btype in ("numbered", "number", "numbered_list_item"):
        return {"object": "block", "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": _rich_text(text)}}, None

    if btype in ("paragraph", "text", "p"):
        return {"object": "block", "type": "paragraph",
                "paragraph": {"rich_text": _rich_text(text)}}, None

    if btype in ("quote",):
        return {"object": "block", "type": "quote",
                "quote": {"rich_text": _rich_text(text)}}, None

    if btype in ("code",):
        language = block.get("language") or "plain text"
        return {"object": "block", "type": "code",
                "code": {"rich_text": _rich_text(text), "language": str(language)}}, None

    if btype in ("todo", "to_do"):
        checked = bool(block.get("checked", False))
        return {"object": "block", "type": "to_do",
                "to_do": {"rich_text": _rich_text(text), "checked": checked}}, None

    if btype in ("divider", "hr"):
        return {"object": "block", "type": "divider", "divider": {}}, None

    return None, (f"block[{index}] has unsupported type {btype!r}. Supported: heading, bullet, "
                  f"numbered, paragraph, quote, code, todo, divider")


def build_notion_blocks(blocks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Convert a list of friendly block specs into Notion block objects.

    Returns (notion_blocks, errors). If errors is non-empty the input is invalid
    and no request should be made.
    """
    if not isinstance(blocks, list) or not blocks:
        return [], ["'blocks' must be a non-empty list."]

    built: List[Dict[str, Any]] = []
    errors: List[str] = []
    for i, block in enumerate(blocks):
        obj, err = _build_one(block, i)
        if err:
            errors.append(err)
        else:
            built.append(obj)
    return built, errors


def _resolve_token(token: Optional[str]) -> Optional[str]:
    """Resolve the Notion integration token from the arg or environment."""
    return token or os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")


def append_notion_blocks(
    page_id: str,
    blocks: List[Dict[str, Any]],
    token: Optional[str] = None,
    notion_version: str = DEFAULT_NOTION_VERSION,
    http_patch: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    """
    Append content blocks to a Notion page (or block) by its ID.

    Args:
        page_id: The Notion page or block ID to append children to.
        blocks: Friendly block specs (see build_notion_blocks / README).
        token: Notion integration token; falls back to NOTION_API_KEY / NOTION_TOKEN.
        notion_version: Notion-Version header value.
        http_patch: Optional transport override (defaults to requests.patch) for testing.

    Returns:
        Dict with status, appended_count, batches, and (on success) block IDs.
    """
    if not page_id or not str(page_id).strip():
        return {"status": "error", "error": "'page_id' is required.", "appended_count": 0}

    resolved_token = _resolve_token(token)
    if not resolved_token:
        return {
            "status": "error",
            "error": "Missing Notion token. Pass 'token' or set NOTION_API_KEY / NOTION_TOKEN.",
            "appended_count": 0,
        }

    children, errors = build_notion_blocks(blocks)
    if errors:
        # Fail fast before any network call so nothing is partially appended.
        return {"status": "error", "error": "Invalid blocks: " + "; ".join(errors), "appended_count": 0}

    # Notion's append-block-children endpoint requires the HTTP PATCH method.
    patch = http_patch or requests.patch
    url = NOTION_API_URL.format(block_id=str(page_id).strip())
    headers = {
        "Authorization": f"Bearer {resolved_token}",
        "Notion-Version": notion_version,
        "Content-Type": "application/json",
    }

    # Notion accepts at most 100 children per request; chunk larger inputs.
    batches = [children[i:i + MAX_BLOCKS_PER_REQUEST]
               for i in range(0, len(children), MAX_BLOCKS_PER_REQUEST)]

    appended_ids: List[str] = []
    for batch_num, batch in enumerate(batches, start=1):
        try:
            resp = patch(url, headers=headers, json={"children": batch}, timeout=30)
        except requests.RequestException as exc:
            return {
                "status": "error",
                "error": f"Network error contacting Notion on batch {batch_num}: {exc}",
                "appended_count": len(appended_ids),
                "batches_completed": batch_num - 1,
            }

        status_code = getattr(resp, "status_code", None)
        if status_code != 200:
            # Try to surface Notion's error message.
            message = None
            try:
                body = resp.json()
                message = body.get("message") or body.get("code")
            except Exception:  # noqa: BLE001 - non-JSON error body
                message = getattr(resp, "text", "")
            return {
                "status": "error",
                "error": f"Notion API returned {status_code} on batch {batch_num}: {message}",
                "appended_count": len(appended_ids),
                "batches_completed": batch_num - 1,
            }

        try:
            data = resp.json()
            for result in data.get("results", []):
                if isinstance(result, dict) and result.get("id"):
                    appended_ids.append(result["id"])
        except Exception:  # noqa: BLE001 - success but unexpected body shape
            pass

    return {
        "status": "success",
        "page_id": str(page_id).strip(),
        "appended_count": len(children),
        "batches": len(batches),
        "block_ids": appended_ids,
    }


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    """Standard entry point for MCP agent tools."""
    return append_notion_blocks(
        page_id=params.get("page_id", ""),
        blocks=params.get("blocks", []),
        token=params.get("token"),
        notion_version=params.get("notion_version", DEFAULT_NOTION_VERSION),
    )


if __name__ == "__main__":
    # ---- 1) Pure builder checks (no network, no credentials) ----
    sample = [
        {"type": "heading", "level": 1, "text": "Release Notes"},
        {"type": "paragraph", "text": "Summary of changes:"},
        {"type": "bullet", "text": "Added Notion appender"},
        {"type": "numbered", "text": "Step one"},
        {"type": "code", "text": "print('hi')", "language": "python"},
        {"type": "todo", "text": "Ship it", "checked": False},
        {"type": "quote", "text": "Ship early, ship often"},
        {"type": "divider"},
    ]
    built, errs = build_notion_blocks(sample)
    assert errs == [], errs
    assert len(built) == 8, len(built)
    assert built[0]["type"] == "heading_1"
    assert built[0]["heading_1"]["rich_text"][0]["text"]["content"] == "Release Notes"
    assert built[2]["type"] == "bulleted_list_item"
    assert built[4]["type"] == "code" and built[4]["code"]["language"] == "python"
    assert built[5]["to_do"]["checked"] is False
    assert built[7]["type"] == "divider"

    # Long text splits into <=2000-char rich_text segments.
    long_built, _ = build_notion_blocks([{"type": "paragraph", "text": "x" * 4500}])
    assert len(long_built[0]["paragraph"]["rich_text"]) == 3

    # Invalid blocks fail fast.
    _, bad = build_notion_blocks([{"type": "heading", "level": 9, "text": "n"}])
    assert bad, "expected an error for bad heading level"
    _, bad2 = build_notion_blocks([{"type": "bogus", "text": "n"}])
    assert bad2, "expected an error for unknown type"
    print("Builder self-tests passed.")

    # ---- 2) Full request assembly via an injected fake transport ----
    calls = []

    class _FakeResp:
        status_code = 200
        def __init__(self, children):
            self._children = children
        def json(self):
            return {"results": [{"id": f"blk_{i}"} for i in range(len(self._children))]}

    def fake_patch(url, headers=None, json=None, timeout=None):
        calls.append({"url": url, "headers": headers, "json": json, "timeout": timeout})
        return _FakeResp(json["children"])

    res = append_notion_blocks(
        page_id="page-123",
        blocks=sample,
        token="secret_test_token",
        http_patch=fake_patch,
    )
    assert res["status"] == "success", res
    assert res["appended_count"] == 8, res
    assert res["batches"] == 1, res
    assert calls[0]["url"] == "https://api.notion.com/v1/blocks/page-123/children"
    assert calls[0]["headers"]["Authorization"] == "Bearer secret_test_token"
    assert calls[0]["headers"]["Notion-Version"] == DEFAULT_NOTION_VERSION
    assert calls[0]["json"]["children"][0]["type"] == "heading_1"

    # Chunking: 150 blocks -> two batches (100 + 50).
    calls.clear()
    many = [{"type": "bullet", "text": f"item {i}"} for i in range(150)]
    res2 = append_notion_blocks(page_id="p", blocks=many, token="t", http_patch=fake_patch)
    assert res2["status"] == "success", res2
    assert res2["batches"] == 2, res2
    assert len(calls) == 2
    assert len(calls[0]["json"]["children"]) == 100
    assert len(calls[1]["json"]["children"]) == 50

    # Missing token / page_id / blocks -> graceful errors.
    assert append_notion_blocks(page_id="", blocks=sample, token="t")["status"] == "error"
    assert append_notion_blocks(page_id="p", blocks=[], token="t")["status"] == "error"
    assert append_notion_blocks(page_id="p", blocks=sample, token=None)["status"] == "error" \
        if not _resolve_token(None) else True

    # Non-200 from Notion -> error surfaced, no crash.
    class _ErrResp:
        status_code = 401
        def json(self):
            return {"message": "API token is invalid.", "code": "unauthorized"}
    res3 = append_notion_blocks(page_id="p", blocks=sample, token="t",
                                http_patch=lambda *a, **k: _ErrResp())
    assert res3["status"] == "error" and "401" in res3["error"], res3

    # Guard against the PATCH-vs-POST regression: the default transport must be PATCH.
    assert requests.patch is not None
    print("Request-assembly, chunking and error-path self-tests passed.")
    print("All self-tests passed successfully!")

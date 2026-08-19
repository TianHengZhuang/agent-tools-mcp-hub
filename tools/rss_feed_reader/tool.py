"""
RSS / Atom Feed Reader Tool for AI Agents
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

USER_AGENT = "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
HTML_TAG_RE = re.compile(r"<[^>]+>")


def _local_tag(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _clean(value: str) -> str:
    return " ".join(HTML_TAG_RE.sub(" ", value).split())


def _text(element: Optional[ET.Element]) -> str:
    if element is None:
        return ""
    chunks = [element.text or ""]
    for child in list(element):
        chunks.append(_text(child))
        chunks.append(child.tail or "")
    return _clean(" ".join(chunks))


def _child(element: ET.Element, name: str) -> Optional[ET.Element]:
    for child in list(element):
        if _local_tag(child.tag) == name:
            return child
    return None


def _children(element: ET.Element, name: str) -> List[ET.Element]:
    return [child for child in list(element) if _local_tag(child.tag) == name]


def _atom_link(entry: ET.Element) -> str:
    fallback = ""
    for link in _children(entry, "link"):
        href = (link.get("href") or "").strip()
        rel = (link.get("rel") or "alternate").lower()
        if rel == "alternate" and href:
            return href
        if href and not fallback:
            fallback = href
    return fallback or _text(_child(entry, "id"))


def _parse_rss_items(root: ET.Element, limit: int) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    channels = _children(root, "channel") or [root]
    for channel in channels:
        for item in _children(channel, "item"):
            items.append(
                {
                    "title": _text(_child(item, "title")),
                    "url": _text(_child(item, "link")) or _text(_child(item, "guid")),
                    "summary": _text(_child(item, "description")) or _text(_child(item, "encoded")),
                    "published": _text(_child(item, "pubDate")) or _text(_child(item, "date")),
                }
            )
            if len(items) >= limit:
                return items
    return items


def _parse_atom_entries(root: ET.Element, limit: int) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    for entry in _children(root, "entry"):
        items.append(
            {
                "title": _text(_child(entry, "title")),
                "url": _atom_link(entry),
                "summary": _text(_child(entry, "summary")) or _text(_child(entry, "content")),
                "published": _text(_child(entry, "published")) or _text(_child(entry, "updated")),
            }
        )
        if len(items) >= limit:
            break
    return items


def read_feed(feed_url: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Fetches an RSS or Atom feed and returns the latest articles.
    """
    if not feed_url or not str(feed_url).strip():
        return {"success": False, "error": "feed_url parameter is required."}

    try:
        limit = int(max_results)
    except (TypeError, ValueError):
        return {"success": False, "error": "max_results must be an integer between 1 and 25."}

    if limit < 1 or limit > 25:
        return {"success": False, "error": "max_results must be an integer between 1 and 25."}

    url = str(feed_url).strip()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return {"success": False, "error": "feed_url must be an http or https URL."}

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = response.read()
            final_url = response.geturl()

        root = ET.fromstring(payload)
        root_name = _local_tag(root.tag).lower()

        if root_name == "rss" or root_name == "rdf":
            articles = _parse_rss_items(root, limit)
            feed_type = "rss"
        elif root_name == "feed":
            articles = _parse_atom_entries(root, limit)
            feed_type = "atom"
        else:
            return {"success": False, "error": f"Unsupported feed format: {root_name}"}

        feed_title = ""
        if root_name == "feed":
            feed_title = _text(_child(root, "title"))
        else:
            channel = _child(root, "channel")
            if channel is not None:
                feed_title = _text(_child(channel, "title"))

        return {
            "success": True,
            "feed_url": final_url or url,
            "feed_title": feed_title,
            "feed_type": feed_type,
            "count": len(articles),
            "articles": articles,
        }
    except urllib.error.HTTPError as e:
        return {"success": False, "error": f"HTTP Error {e.code}: {e.reason}"}
    except ET.ParseError as e:
        return {"success": False, "error": f"Failed to parse feed XML: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to read feed: {str(e)}"}


if __name__ == "__main__":
    result = read_feed("https://hnrss.org/frontpage", max_results=5)
    print(json.dumps(result, indent=2))

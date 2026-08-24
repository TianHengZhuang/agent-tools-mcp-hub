"""Create Notion database pages and append text blocks to pages."""

from typing import Any, Dict, Iterable, List, Optional
import os

import requests


NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers(token: str) -> Dict[str, str]:
	return {
		"Authorization": f"Bearer {token}",
		"Notion-Version": NOTION_VERSION,
		"Content-Type": "application/json",
	}


def _text_block(text: str, bullet: bool = False) -> Dict[str, Any]:
	"""Build one valid Notion paragraph or bulleted-list block."""
	block_type = "bulleted_list_item" if bullet else "paragraph"
	return {
		"object": "block",
		"type": block_type,
		block_type: {
			"rich_text": [{"type": "text", "text": {"content": str(text)}}]
		},
	}


def _response_result(response: requests.Response) -> Dict[str, Any]:
	try:
		response.raise_for_status()
	except requests.HTTPError as exc:
		try:
			details = response.json()
		except ValueError:
			details = response.text
		return {
			"success": False,
			"error": f"Notion API request failed: {exc}",
			"details": details,
		}

	try:
		return {"success": True, "data": response.json()}
	except ValueError:
		return {"success": True, "data": {}}


def create_notion_page(
	database_id: str,
	title: str,
	properties: Optional[Dict[str, Any]] = None,
	blocks: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
	"""Create a new page in a Notion database."""
	token = os.getenv("NOTION_TOKEN")
	if not token:
		return {"success": False, "error": "NOTION_TOKEN is not set."}
	if not database_id or not title:
		return {"success": False, "error": "database_id and title are required."}

	page_properties = dict(properties or {})
	page_properties.setdefault(
		"title", {"title": [{"type": "text", "text": {"content": title}}]}
	)
	payload: Dict[str, Any] = {
		"parent": {"database_id": database_id},
		"properties": page_properties,
	}
	if blocks:
		payload["children"] = list(blocks)

	try:
		response = requests.post(
			f"{NOTION_API_URL}/pages",
			headers=_headers(token),
			json=payload,
			timeout=30,
		)
	except requests.RequestException as exc:
		return {"success": False, "error": f"Unable to reach Notion: {exc}"}
	return _response_result(response)


def append_text_blocks(
	page_id: str,
	texts: Iterable[str],
	bullets: bool = False,
) -> Dict[str, Any]:
	"""Append paragraph or bulleted text blocks to an existing Notion page."""
	token = os.getenv("NOTION_TOKEN")
	if not token:
		return {"success": False, "error": "NOTION_TOKEN is not set."}
	if not page_id:
		return {"success": False, "error": "page_id is required."}

	children = [_text_block(text, bullet=bullets) for text in texts]
	if not children:
		return {"success": False, "error": "texts must contain at least one item."}
	payload = {"children": children}

	try:
		response = requests.patch(
			f"{NOTION_API_URL}/blocks/{page_id}/children",
			headers=_headers(token),
			json=payload,
			timeout=30,
		)
	except requests.RequestException as exc:
		return {"success": False, "error": f"Unable to reach Notion: {exc}"}
	return _response_result(response)


def run_tool(
	action: str,
	database_id: str = "",
	title: str = "",
	page_id: str = "",
	texts: Optional[Iterable[str]] = None,
	bullets: bool = False,
	properties: Optional[Dict[str, Any]] = None,
	blocks: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
	"""Dispatch a page creation or text append operation."""
	if action == "create_page":
		return create_notion_page(database_id, title, properties, blocks)
	if action == "append_blocks":
		return append_text_blocks(page_id, texts or [], bullets)
	return {"success": False, "error": "action must be create_page or append_blocks."}


def run(params: Dict[str, Any]) -> Dict[str, Any]:
	"""Standard repository entry point for dictionary-based callers."""
	return run_tool(**params)

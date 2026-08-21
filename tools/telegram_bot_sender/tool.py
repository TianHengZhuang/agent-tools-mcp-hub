"""
Telegram Bot Message Sender Tool

Sends text messages to a Telegram chat using the Telegram Bot API.
"""

import os
from typing import Any, Dict

import requests


TELEGRAM_API_BASE = "https://api.telegram.org"


def run_tool(query: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Send a text message to a Telegram chat.

    Args:
        query (str): Message text to send.
        chat_id (str): Telegram chat, group, or channel ID.

    Environment Variables:
        TELEGRAM_BOT_TOKEN: Telegram Bot API token.

    Returns:
        Dict[str, Any]: Result containing success status and response data.
    """

    if not query or not query.strip():
        return {
            "success": False,
            "error": "Message cannot be empty.",
        }

    chat_id = kwargs.get("chat_id")

    if not chat_id:
        return {
            "success": False,
            "error": "chat_id is required.",
        }

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        return {
            "success": False,
            "error": "TELEGRAM_BOT_TOKEN environment variable is not set.",
        }

    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": query.strip(),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            return {
                "success": False,
                "error": data.get(
                    "description",
                    "Telegram API returned an unsuccessful response.",
                ),
            }

        result = data.get("result", {})

        return {
            "success": True,
            "data": {
                "message_id": result.get("message_id"),
                "chat_id": result.get("chat", {}).get("id"),
                "text": result.get("text"),
            },
        }

    except requests.RequestException as exc:
        return {
            "success": False,
            "error": f"Telegram API request failed: {exc}",
        }
"""
Telegram Bot Notification Tool for AI Agents and MCP Hub.
Sends messages, alerts, and notifications to Telegram chats or channels.
"""
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Union


def send_telegram_notification(
    message: str,
    chat_id: Optional[Union[str, int]] = None,
    bot_token: Optional[str] = None,
    parse_mode: str = "Markdown",
    disable_web_page_preview: bool = False,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Sends a message to a Telegram chat, group, or channel via Telegram Bot API.

    Args:
        message (str): Text content of the message to send.
        chat_id (str | int, optional): Telegram chat ID or channel username (@channel).
            Defaults to TELEGRAM_CHAT_ID environment variable.
        bot_token (str, optional): Telegram Bot API token from @BotFather.
            Defaults to TELEGRAM_BOT_TOKEN environment variable.
        parse_mode (str): Formatting mode ('Markdown', 'MarkdownV2', or 'HTML'). Default 'Markdown'.
        disable_web_page_preview (bool): If True, link previews will be disabled.

    Returns:
        Dict[str, Any]: Result dictionary containing success status, response data, or error message.
    """
    token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    target_chat = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    if not token:
        return {
            "success": False,
            "error": "Telegram Bot Token is required. Pass bot_token parameter or set TELEGRAM_BOT_TOKEN environment variable."
        }

    if not target_chat:
        return {
            "success": False,
            "error": "Telegram Chat ID is required. Pass chat_id parameter or set TELEGRAM_CHAT_ID environment variable."
        }

    if not message or not str(message).strip():
        return {
            "success": False,
            "error": "Message parameter cannot be empty."
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": str(target_chat).strip(),
        "text": str(message).strip(),
        "disable_web_page_preview": bool(disable_web_page_preview)
    }

    if parse_mode:
        payload["parse_mode"] = parse_mode

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "AgentToolsHub/1.0 (https://github.com/tarunjandra/agent-tools-mcp-hub)"
    }

    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=15) as resp:
            status_code = resp.getcode()
            response_body = resp.read().decode("utf-8")
            data = json.loads(response_body)

        if data.get("ok"):
            result = data.get("result", {})
            return {
                "success": True,
                "message": "Telegram notification sent successfully.",
                "data": {
                    "message_id": result.get("message_id"),
                    "chat": result.get("chat"),
                    "date": result.get("date")
                }
            }
        else:
            return {
                "success": False,
                "error": data.get("description", "Unknown Telegram API error"),
                "error_code": data.get("error_code")
            }

    except urllib.error.HTTPError as e:
        error_msg = f"HTTP Error {e.code}: {e.reason}"
        try:
            body = e.read().decode("utf-8")
            error_json = json.loads(body)
            if "description" in error_json:
                error_msg = f"Telegram API Error ({e.code}): {error_json['description']}"
        except Exception:
            pass
        return {
            "success": False,
            "error": error_msg
        }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Network connection error: {str(e.reason)}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error while sending Telegram notification: {str(e)}"
        }


def run_tool(query: str = "", **kwargs: Any) -> Dict[str, Any]:
    """
    Standard agent dispatcher entrypoint.
    Accepts 'message' (or 'query' as fallback) along with other optional parameters.
    """
    message = kwargs.get("message") or query
    chat_id = kwargs.get("chat_id")
    bot_token = kwargs.get("bot_token")
    parse_mode = kwargs.get("parse_mode", "Markdown")
    disable_web_page_preview = kwargs.get("disable_web_page_preview", False)

    return send_telegram_notification(
        message=message,
        chat_id=chat_id,
        bot_token=bot_token,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview
    )


if __name__ == "__main__":
    print("Telegram Notifier Tool loaded.")
    print("Example invocation with missing token (expected graceful error handling):")
    result = run_tool("Hello from Agent Tools Hub!")
    print(json.dumps(result, indent=2))

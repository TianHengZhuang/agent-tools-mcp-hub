"""
Slack Webhook Notification Tool for AI Agents
"""
import os
import urllib.request
import json
from typing import Dict, Any, Optional

def send_slack_notification(message: str, webhook_url: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
    """
    Sends a structured notification block to a Slack channel via Incoming Webhook.
    """
    target_webhook = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not target_webhook:
        return {
            "success": False,
            "error": "No Slack Webhook URL provided. Supply webhook_url parameter or set SLACK_WEBHOOK_URL environment variable."
        }

    if not message or not message.strip():
        return {
            "success": False,
            "error": "Message cannot be empty."
        }

    blocks = []
    if title:
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title[:150],
                "emoji": True
            }
        })
        
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    })

    payload = {
        "text": f"{title + ': ' if title else ''}{message}",
        "blocks": blocks
    }

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            target_webhook,
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.getcode()
            
        return {
            "success": True,
            "status_code": status_code,
            "message": "Slack notification sent successfully."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send Slack alert: {str(e)}"
        }

if __name__ == "__main__":
    print("Slack tool loaded. Test by setting SLACK_WEBHOOK_URL.")

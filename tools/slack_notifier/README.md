# Slack Notifier Tool

Send structured alerts, markdown updates, and agent status messages to any Slack channel using Incoming Webhooks.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `string` | Yes | Markdown content to send |
| `webhook_url` | `string` | No | Slack Webhook URL (reads `SLACK_WEBHOOK_URL` by default) |
| `title` | `string` | No | Header text for the notification |

## Usage

```python
from tool import send_slack_notification

send_slack_notification(
    title="Agent Status Alert 🚨",
    message="Analysis finished with *0 errors* across 45 repositories.",
    webhook_url="https://hooks.slack.com/services/..."
)
```

# Telegram Notifier Tool

Sends structured messages, markdown alerts, and notifications directly to Telegram chats, groups, or channels using the Telegram Bot API.

## Features
- 🚀 **Zero external dependencies**: Built purely with Python standard library (`urllib`).
- 💬 **Flexible targeting**: Send to private chats, group chats, or broadcast channels (via chat ID or `@channel_username`).
- 🎨 **Rich text formatting**: Supports `Markdown`, `MarkdownV2`, and `HTML` parse modes.
- 🔐 **Secure credentials**: Seamlessly reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from environment variables or parameter inputs.

---

## ⚙️ Setup & Prerequisites

1. **Create a Telegram Bot**:
   - Open Telegram and message [@BotFather](https://t.me/BotFather).
   - Send `/newbot` and follow the instructions to get your **Bot Token** (e.g., `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`).

2. **Get your Chat ID**:
   - For personal chat: Message [@userinfobot](https://t.me/userinfobot) to get your numerical Chat ID (e.g., `987654321`).
   - For channels/groups: Add your bot as an administrator and use the channel username (e.g., `@my_channel_name`) or channel ID.

3. *(Optional)* Export environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_CHAT_ID="your_chat_id_here"
   ```

---

## 📥 Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `message` | `string` | **Yes** | The text message content to send (supports Markdown or HTML). |
| `chat_id` | `string` / `integer` | No | Target Chat ID or `@channel` username. Defaults to `TELEGRAM_CHAT_ID` env var. |
| `bot_token` | `string` | No | Telegram Bot Token. Defaults to `TELEGRAM_BOT_TOKEN` env var. |
| `parse_mode` | `string` | No | Formatting mode: `"Markdown"`, `"MarkdownV2"`, or `"HTML"`. Default is `"Markdown"`. |
| `disable_web_page_preview` | `boolean` | No | Disables link preview generation. Default is `false`. |

---

## 💻 Usage Example

### Python

```python
from tool import send_telegram_notification

# Example 1: Basic notification using environment variables
result = send_telegram_notification(
    message="🚀 *Deployment Alert*: Pipeline succeeded with 0 errors!"
)
print(result)

# Example 2: Explicit parameters with HTML formatting
result = send_telegram_notification(
    message="<b>System Alert</b>: Server load exceeded <i>85%</i>.",
    chat_id="123456789",
    bot_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
    parse_mode="HTML"
)
print(result)
```

---

## 📤 Example Response

### Success:
```json
{
  "success": true,
  "message": "Telegram notification sent successfully.",
  "data": {
    "message_id": 1024,
    "chat": {
      "id": 987654321,
      "first_name": "Alireza",
      "type": "private"
    },
    "date": 1700000000
  }
}
```

### Error:
```json
{
  "success": false,
  "error": "Telegram Bot Token is required. Pass bot_token parameter or set TELEGRAM_BOT_TOKEN environment variable."
}
```

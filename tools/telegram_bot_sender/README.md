# Telegram Bot Message Sender

Send text messages and agent alerts to Telegram chats using the Telegram Bot API.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | string | Yes | Message text to send |
| `chat_id` | string | Yes | Telegram chat, group, or channel ID |

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram Bot API token |

## Installation

```bash
pip install -r requirements.txt
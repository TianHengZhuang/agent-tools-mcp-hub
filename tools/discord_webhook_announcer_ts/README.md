# Discord Webhook Announcer (TypeScript)

Sends notifications and rich embed announcements to Discord channels using Discord webhooks.

## Features

- Send Discord webhook notifications
- Rich embed title and description
- Custom webhook username
- Custom embed color
- Automatic timestamp
- Input validation
- Error handling
- No additional API key required beyond the Discord webhook URL

## Installation

```bash
npm install
```

## Build

```bash
npm run build
```

## Usage

```typescript
import { sendDiscordAnnouncement } from "./index";

const result = await sendDiscordAnnouncement(
  process.env.DISCORD_WEBHOOK_URL!,
  "Deployment completed successfully.",
  "Production Update"
);

console.log(result);
```

## Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| webhookUrl | string | Yes | Discord webhook URL |
| message | string | Yes | Announcement message |
| title | string | No | Embed title |
| username | string | No | Webhook display name |
| color | number | No | Discord embed color |

## Security

Never commit Discord webhook URLs to source control. Store webhook URLs in environment variables or a secrets manager.

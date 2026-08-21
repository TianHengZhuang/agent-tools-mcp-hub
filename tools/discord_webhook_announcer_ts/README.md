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

## Agent / MCP entry point

`runTool` takes a single params object matching the `parameters` schema in
`metadata.json` — the shape an MCP server or agent framework passes in:

```typescript
import { runTool } from "./index";

const result = await runTool({
  webhookUrl: process.env.DISCORD_WEBHOOK_URL!,
  message: "Deployment completed successfully.",
  title: "Production Update"
});
// -> { success: true, status: 204, message: "Discord announcement sent successfully." }
```

On failure it resolves (never throws) to `{ success: false, error: "..." }`,
with `status` included when Discord returned an HTTP error.

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

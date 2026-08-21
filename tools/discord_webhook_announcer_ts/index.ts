/**
 * Discord Webhook Announcer Tool - TypeScript Implementation
 */

interface DiscordWebhookResult {
  success: boolean;
  status?: number;
  message?: string;
  error?: string;
}

interface DiscordEmbed {
  title?: string;
  description: string;
  color?: number;
  timestamp?: string;
}

async function sendDiscordAnnouncement(
  webhookUrl: string,
  message: string,
  title: string = "Announcement",
  username: string = "Agent Tools Hub",
  color: number = 3447003
): Promise<DiscordWebhookResult> {
  if (!webhookUrl || !webhookUrl.trim()) {
    return {
      success: false,
      error: "Discord webhook URL is required."
    };
  }

  if (!message || !message.trim()) {
    return {
      success: false,
      error: "Message is required."
    };
  }

  const normalizedUrl = webhookUrl.trim();

  if (
    !normalizedUrl.startsWith("https://discord.com/api/webhooks/") &&
    !normalizedUrl.startsWith("https://discordapp.com/api/webhooks/")
  ) {
    return {
      success: false,
      error: "Invalid Discord webhook URL."
    };
  }

  const embed: DiscordEmbed = {
    title,
    description: message,
    color,
    timestamp: new Date().toISOString()
  };

  const payload = {
    username,
    embeds: [embed]
  };

  try {
    const response = await fetch(normalizedUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "User-Agent": "AgentToolsHub/1.0"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error: `Discord webhook failed: HTTP ${response.status} ${response.statusText}`
      };
    }

    return {
      success: true,
      status: response.status,
      message: "Discord announcement sent successfully."
    };
  } catch (error) {
    return {
      success: false,
      error: `Discord webhook error: ${
        error instanceof Error ? error.message : String(error)
      }`
    };
  }
}

async function runTool(
  webhookUrl: string,
  message: string,
  title: string = "Announcement",
  username: string = "Agent Tools Hub",
  color: number = 3447003
): Promise<DiscordWebhookResult> {
  return sendDiscordAnnouncement(
    webhookUrl,
    message,
    title,
    username,
    color
  );
}

export {
  sendDiscordAnnouncement,
  runTool
};

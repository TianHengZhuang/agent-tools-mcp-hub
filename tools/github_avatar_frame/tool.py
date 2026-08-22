"""Generate framed GitHub avatars with the public GitHub Avatar Frame API."""

import base64
import re
from typing import Any, Dict, Optional, Set
from urllib.parse import quote

import requests


API_BASE_URL = "https://github-avatar-frame-api.onrender.com/api/framed-avatar"
UPSTREAM_REPOSITORY_URL = "https://github.com/TechQuanta/github-avatar-frame-api"
UPSTREAM_FRAMES_DIRECTORY_URL = f"{UPSTREAM_REPOSITORY_URL}/tree/main/public/frames"
FRAMES_DIRECTORY_API_URL = (
    "https://api.github.com/repos/TechQuanta/github-avatar-frame-api/"
    "contents/public/frames?ref=main"
)
GITHUB_USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
CANVASES = {"light", "dark", "transparent"}
SHAPES = {"circle", "rounded", "rect"}
FORMATS = {"png", "jpg", "svg"}


def get_available_themes() -> Optional[Set[str]]:
    """Return the current frame-directory names from the upstream repository."""
    try:
        response = requests.get(
            FRAMES_DIRECTORY_API_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "agent-tools-mcp-hub",
            },
            timeout=10,
        )
        response.raise_for_status()
        entries = response.json()
    except (requests.RequestException, ValueError):
        return None

    if not isinstance(entries, list):
        return None
    return {
        entry["name"].strip().lower()
        for entry in entries
        if isinstance(entry, dict)
        and entry.get("type") == "dir"
        and isinstance(entry.get("name"), str)
    }


def run_tool(
    username: str,
    theme: str = "base",
    size: int = 256,
    canvas: str = "light",
    shape: str = "circle",
    radius: int = 25,
    output_format: str = "png",
    text: Optional[str] = None,
    text_color: str = "#ffffff",
    text_size: int = 20,
    text_position: str = "bottom",
    emojis: Optional[str] = None,
    emoji_size: int = 40,
    emoji_position: str = "top",
    **_: Any,
) -> Dict[str, Any]:
    """Fetch a framed GitHub avatar and return its URL and base64-encoded image."""
    normalized_username = (username or "").strip()
    if not normalized_username:
        return {"success": False, "error": "username cannot be empty."}
    if not GITHUB_USERNAME_PATTERN.fullmatch(normalized_username):
        return {
            "success": False,
            "error": "username must be a valid GitHub username of up to 39 letters, digits, or hyphens.",
        }
    if not isinstance(size, int) or not 64 <= size <= 1024:
        return {"success": False, "error": "size must be an integer between 64 and 1024."}
    if not isinstance(radius, int) or not 0 <= radius <= 1024:
        return {"success": False, "error": "radius must be an integer between 0 and 1024."}
    if not isinstance(text_size, int) or not 8 <= text_size <= 100:
        return {"success": False, "error": "text_size must be an integer between 8 and 100."}
    if not isinstance(emoji_size, int) or not 16 <= emoji_size <= 120:
        return {"success": False, "error": "emoji_size must be an integer between 16 and 120."}

    normalized_theme = theme.lower().strip()
    normalized_canvas = canvas.lower().strip()
    normalized_shape = shape.lower().strip()
    normalized_format = output_format.lower().strip()
    if not normalized_theme:
        return {"success": False, "error": "theme cannot be empty."}
    if normalized_canvas not in CANVASES:
        return {"success": False, "error": "canvas must be light, dark, or transparent."}
    if normalized_shape not in SHAPES:
        return {"success": False, "error": "shape must be circle, rounded, or rect."}
    if normalized_format not in FORMATS:
        return {"success": False, "error": "output_format must be png, jpg, or svg."}
    if text_position not in {"top", "bottom", "center"}:
        return {"success": False, "error": "text_position must be top, bottom, or center."}
    if emoji_position not in {"top", "bottom", "corners"}:
        return {"success": False, "error": "emoji_position must be top, bottom, or corners."}

    available_themes = get_available_themes()
    if available_themes and normalized_theme not in available_themes:
        return {
            "success": False,
            "error": "theme is not available upstream. Available themes: "
            f"{', '.join(sorted(available_themes))}.",
        }

    params = {
        "theme": normalized_theme,
        "size": size,
        "canvas": normalized_canvas,
        "shape": normalized_shape,
        "radius": radius,
        "format": normalized_format,
        "textColor": text_color,
        "textSize": text_size,
        "textPosition": text_position,
        "emojiSize": emoji_size,
        "emojiPosition": emoji_position,
    }
    if text:
        params["text"] = text
    if emojis:
        params["emojis"] = emojis

    try:
        response = requests.get(
            f"{API_BASE_URL}/{normalized_username}",
            params=params,
            headers={"User-Agent": "agent-tools-mcp-hub"},
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"success": False, "error": f"GitHub Avatar Frame API request failed: {exc}"}

    mime_type = response.headers.get("Content-Type", "image/png").split(";", 1)[0]
    if not mime_type.startswith("image/"):
        return {"success": False, "error": "GitHub Avatar Frame API returned a non-image response."}

    encoded_username = quote(normalized_username, safe="")
    urls = {
        "generated_framed_avatar": response.url,
        "original_github_avatar": f"https://github.com/{encoded_username}.png?size={size}",
        "github_profile": f"https://github.com/{encoded_username}",
        "frame_catalog": UPSTREAM_FRAMES_DIRECTORY_URL,
        "frame_api": API_BASE_URL,
        "source_repository": UPSTREAM_REPOSITORY_URL,
    }

    return {
        "success": True,
        "data": {
            "username": normalized_username,
            "image_url": response.url,
            "urls": urls,
            "image_base64": base64.b64encode(response.content).decode("ascii"),
            "mime_type": mime_type,
            "size_pixels": size,
            "theme": normalized_theme,
            "available_themes": sorted(available_themes) if available_themes else None,
            "canvas": normalized_canvas,
            "shape": normalized_shape,
            "output_format": normalized_format,
        },
    }


if __name__ == "__main__":
    result = run_tool(username="octocat", theme="flamingo", size=512)
    print({key: value for key, value in result.items() if key != "data"})
    if result["success"]:
        print(result["data"]["image_url"])

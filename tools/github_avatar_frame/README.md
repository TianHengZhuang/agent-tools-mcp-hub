# GitHub Avatar Frame Generator

Generate a themed frame around any public GitHub avatar with the free [GitHub Avatar Frame API](https://github-avatar-frame-api.onrender.com). The tool returns base64 image data and a set of URLs so callers can choose the destination they need.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `username` | `string` | Yes | GitHub username whose avatar will be framed |
| `theme` | `string` | No | Frame theme. Names are loaded from the upstream [`public/frames`](https://github.com/TechQuanta/github-avatar-frame-api/tree/main/public/frames) directory at runtime (default `base`) |
| `size` | `integer` | No | Image size from 64 to 1024 pixels (default `256`) |
| `canvas` | `string` | No | `light`, `dark`, or `transparent` (default `light`) |
| `shape` | `string` | No | `circle`, `rounded`, or `rect` (default `circle`) |
| `radius` | `integer` | No | Corner radius for `rounded` or `rect` (default `25`) |
| `output_format` | `string` | No | `png`, `jpg`, or `svg` (default `png`) |
| `text` | `string` | No | Text overlay |
| `text_color` | `string` | No | Hexadecimal text color (default `#ffffff`) |
| `text_size` | `integer` | No | Text size from 8 to 100 pixels (default `20`) |
| `text_position` | `string` | No | `top`, `bottom`, or `center` (default `bottom`) |
| `emojis` | `string` | No | Comma-separated emoji overlays |
| `emoji_size` | `integer` | No | Emoji size from 16 to 120 pixels (default `40`) |
| `emoji_position` | `string` | No | `top`, `bottom`, or `corners` (default `top`) |

## Installation & Setup

```bash
pip install -r requirements.txt
```

No API key is required. This tool calls the public GitHub Avatar Frame API and looks up current frame-directory names from the upstream GitHub repository. If GitHub is temporarily unavailable, generation still proceeds and the Avatar Frame API remains the final authority on valid theme names.

## Returned URLs

The `data.urls` object contains these choices:

| Key | Destination |
| :--- | :--- |
| `generated_framed_avatar` | The generated framed image with all selected options |
| `original_github_avatar` | The original, unframed GitHub avatar image |
| `github_profile` | The user's GitHub profile page |
| `frame_catalog` | The upstream directory containing current frame themes |
| `frame_api` | The GitHub Avatar Frame API base endpoint |
| `source_repository` | The upstream GitHub Avatar Frame API repository |

## Usage Example

```python
from tool import run_tool

result = run_tool(
    username="octocat",
    theme="flamingo",
    size=512,
    canvas="dark",
    shape="rounded",
    radius=24,
    text="Open Source",
    emojis="🚀,💻",
    emoji_position="corners",
)

if result["success"]:
    for url_type, url in result["data"]["urls"].items():
        print(f"{url_type}: {url}")

    import base64
    with open("octocat-frame.png", "wb") as image_file:
        image_file.write(base64.b64decode(result["data"]["image_base64"]))
```

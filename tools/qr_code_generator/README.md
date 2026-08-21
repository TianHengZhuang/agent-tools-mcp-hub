# QR Code Generator Tool

Generate QR code images from any text, URL, or data string. Returns a base64-encoded PNG image suitable for embedding in HTML, saving to disk, or passing to downstream agents.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `data` | `string` | Yes | The text, URL, or data to encode into a QR code |
| `size` | `integer` | No | Size of the output image in pixels (64–2048, default 256) |
| `error_correction` | `string` | No | Error correction level: L (7%), M (15%), Q (25%), H (30%). Default M |

## Installation & Setup

```bash
pip install -r requirements.txt
```

No API keys or external services required.

## Usage Example

```python
from tool import run_tool

result = run_tool(data="https://example.com", size=512, error_correction="H")
if result["success"]:
    # Save to file
    import base64
    with open("qrcode.png", "wb") as f:
        f.write(base64.b64decode(result["data"]["image_base64"]))

    # Or embed in HTML
    html_img = f'<img src="data:{result["data"]["mime_type"]};base64,{result["data"]["image_base64"]}" />'
```

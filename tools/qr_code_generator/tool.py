"""
QR Code Generator Tool
Generates QR code images from URLs or text strings using the qrcode library.
"""
import base64
import io
from typing import Any, Dict

import qrcode
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)

ERROR_CORRECTION_MAP = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}


def run_tool(
    data: str, size: int = 256, error_correction: str = "M", **kwargs: Any
) -> Dict[str, Any]:
    """
    Generate a QR code image for the given data.

    Args:
        data: The text, URL, or data to encode.
        size: Size of the output image in pixels.
        error_correction: Error correction level (L, M, Q, H).

    Returns:
        Dict with success status and base64-encoded PNG image data.
    """
    if not data or not data.strip():
        return {"success": False, "error": "Data parameter cannot be empty."}

    if size < 64 or size > 2048:
        return {"success": False, "error": "Size must be between 64 and 2048 pixels."}

    ec_level = ERROR_CORRECTION_MAP.get(error_correction.upper())
    if ec_level is None:
        return {
            "success": False,
            "error": f"Invalid error correction level '{error_correction}'. Use L, M, Q, or H.",
        }

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ec_level,
            box_size=10,
            border=4,
        )
        qr.add_data(data.strip())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        b64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return {
            "success": True,
            "data": {
                "image_base64": b64_image,
                "mime_type": "image/png",
                "size_pixels": size,
                "error_correction": error_correction.upper(),
                "encoded_data": data.strip(),
            },
        }
    except Exception as e:
        return {"success": False, "error": f"QR code generation failed: {str(e)}"}


if __name__ == "__main__":
    import json

    result = run_tool("https://github.com/tarunjandra/agent-tools-mcp-hub")
    print(json.dumps({k: v for k, v in result.items() if k != "data"}, indent=2))
    if result["success"]:
        print(f"Generated QR code: {result['data']['size_pixels']}px, EC={result['data']['error_correction']}")
        print(f"Base64 length: {len(result['data']['image_base64'])} chars")

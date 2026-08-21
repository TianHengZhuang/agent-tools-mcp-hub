"""
PDF Text Extractor Tool
"""

from typing import Dict, Any
from pypdf import PdfReader


def run_tool(file_path: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Extract plain text from a local PDF file.

    Args:
        file_path (str): Path to the local PDF file.

    Returns:
        Dict[str, Any]: Result containing extracted text or an error.
    """
    if not file_path:
        return {
            "success": False,
            "error": "file_path parameter cannot be empty."
        }

    try:
        reader = PdfReader(file_path)

        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        extracted_text = "\n".join(pages).strip()

        return {
            "success": True,
            "data": {
                "text": extracted_text,
                "pages": len(reader.pages)
            }
        }

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)
        }


if __name__ == "__main__":
    print("PDF Text Extractor Tool")

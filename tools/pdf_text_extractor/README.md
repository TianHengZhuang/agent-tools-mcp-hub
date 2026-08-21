# PDF Text Extractor

A Python tool that extracts plain text from local PDF files using `pypdf`.

## Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `file_path` | string | Yes | Path to the local PDF file |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from tool import run_tool

result = run_tool("example.pdf")
print(result)
```

## Output

The tool returns the extracted text and the number of pages.

## Error Handling

Returns `success: false` with an error message if the PDF cannot be read.

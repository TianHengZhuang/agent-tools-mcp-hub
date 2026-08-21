# Google Gemini / Vertex AI Embeddings

Generate text embeddings for semantic search using the Google Generative AI Python SDK.

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `query` | `string` | Yes* | Text to embed |
| `texts` | `array` | No | Batch of texts (used instead of `query` if provided) |
| `model` | `string` | No | Default: `models/text-embedding-004` |
| `task_type` | `string` | No | Default: `retrieval_document` |
| `title` | `string` | No | Optional title for `retrieval_document` |
| `provider` | `string` | No | `gemini` (default) or `vertex` |

\* Required unless `texts` is provided.

## Installation & Setup

```bash
pip install -r requirements.txt
```

Set one of these environment variables:

```bash
set GOOGLE_API_KEY=your-gemini-api-key
```

For Vertex AI:

```bash
set GOOGLE_CLOUD_PROJECT=your-gcp-project
set GOOGLE_CLOUD_LOCATION=us-central1
```

## Usage Example

```python
from tool import run_tool

response = run_tool(query="What is Model Context Protocol?")
print(response["success"])
print(len(response["data"]["embeddings"][0]))
```

Batch example:

```python
from tool import run_tool

response = run_tool(
    query="",
    texts=["first document", "second document"],
    task_type="retrieval_document",
)
print(response)
```

# Notion Page & Database Block Appender

Append structured content blocks — headings, bulleted / numbered lists, code blocks, paragraphs, quotes, to-dos and dividers — to a Notion page (or any block that accepts children) using the [Notion REST API](https://developers.notion.com/reference/patch-block-children).

## Features

- **Rich block types**: `heading` (levels 1–3), `bullet`, `numbered`, `paragraph`, `quote`, `code` (with language), `todo` (with checked state), and `divider` — via a simple, friendly input schema (no need to hand-write Notion's verbose block JSON).
- **Respects Notion's API limits automatically**:
  - Chunks appends into batches of **100 blocks per request** (Notion's max).
  - Splits any text longer than **2000 characters** into multiple `rich_text` segments (Notion's per-object cap).
- **Fail-fast validation**: all blocks are validated *before* any network call, so an invalid block never results in a partial append.
- **Safe secret handling**: reads the integration token from the `token` parameter or the `NOTION_API_KEY` / `NOTION_TOKEN` environment variables — never hardcoded.
- **Graceful errors**: clear messages for missing token/page, invalid blocks, network failures, and non-200 responses (surfacing Notion's own error message).

## Setup

```bash
pip install -r requirements.txt
```

1. Create an integration at <https://www.notion.so/my-integrations> and copy its **Internal Integration Token**.
2. **Share the target page** with your integration (in Notion: page → `•••` → *Connections* → add your integration), otherwise the API returns a 404/permission error.
3. Export the token:
   ```bash
   export NOTION_API_KEY="secret_xxx"
   ```

## Parameters

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `page_id` | `string` | **Yes** | — | The Notion page or block ID to append children to |
| `blocks` | `array` | **Yes** | — | List of block specs (see below) |
| `token` | `string` | No | env vars | Notion integration token (falls back to `NOTION_API_KEY` / `NOTION_TOKEN`) |
| `notion_version` | `string` | No | `2022-06-28` | `Notion-Version` header value |

### Block spec format

| `type` | Fields | Example |
|---|---|---|
| `heading` | `level` (1–3), `text` | `{"type": "heading", "level": 2, "text": "Overview"}` |
| `bullet` | `text` | `{"type": "bullet", "text": "First point"}` |
| `numbered` | `text` | `{"type": "numbered", "text": "Step one"}` |
| `paragraph` | `text` | `{"type": "paragraph", "text": "Some prose."}` |
| `quote` | `text` | `{"type": "quote", "text": "A memorable line"}` |
| `code` | `text`, `language` | `{"type": "code", "text": "print(1)", "language": "python"}` |
| `todo` | `text`, `checked` | `{"type": "todo", "text": "Do it", "checked": false}` |
| `divider` | — | `{"type": "divider"}` |

## Usage Example

```python
from tool import run

response = run({
    "page_id": "2f1c8b3a4d5e6f708192a3b4c5d6e7f8",
    "blocks": [
        {"type": "heading", "level": 1, "text": "Release Notes"},
        {"type": "paragraph", "text": "Highlights from this release:"},
        {"type": "bullet", "text": "New Notion appender tool"},
        {"type": "bullet", "text": "Automatic batching & rich-text splitting"},
        {"type": "code", "text": "run({'page_id': '...', 'blocks': [...]})", "language": "python"},
        {"type": "todo", "text": "Announce in changelog", "checked": False},
        {"type": "divider"},
    ],
})
print(response)
```

### Response Format
```json
{
  "status": "success",
  "page_id": "2f1c8b3a4d5e6f708192a3b4c5d6e7f8",
  "appended_count": 7,
  "batches": 1,
  "block_ids": ["blk_...", "blk_..."]
}
```

### Error Response
```json
{
  "status": "error",
  "error": "Notion API returned 401 on batch 1: API token is invalid.",
  "appended_count": 0,
  "batches_completed": 0
}
```

## Running the Self-Test

`tool.py` includes a self-test that runs **fully offline** — it checks the pure block-builder for every block type, verifies text-splitting and validation, and exercises the complete request-assembly, 100-block batching, and error paths through an injected fake HTTP transport (no Notion account required):

```bash
python tool.py
```

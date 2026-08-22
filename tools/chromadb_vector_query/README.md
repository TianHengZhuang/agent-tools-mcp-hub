# ChromaDB Vector Store Query

Run **read-only** semantic similarity searches against a local (persistent) ChromaDB vector database.

- Query by **natural-language text** or by a **pre-computed embedding vector**
- Optional **metadata** and **document-content** filters
- Returns ranked matches with documents, metadata, raw distance **and** a normalised similarity score
- Never creates, modifies or deletes collections

## Parameters

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `collection` | `string` | Yes | Name of the Chroma collection to search |
| `query` | `string` | No\* | Natural-language search text, embedded with the collection's own embedding function |
| `query_embedding` | `array[number]` | No\* | Pre-computed vector. Use instead of `query` when embeddings are generated externally |
| `db_path` | `string` | No | Path to the persistent Chroma directory (default `./chroma_db`) |
| `n_results` | `integer` | No | Number of matches to return, 1–100 (default `5`) |
| `where` | `object` | No | Metadata filter, e.g. `{"type": "finance"}` |
| `where_document` | `object` | No | Document content filter, e.g. `{"$contains": "invoice"}` |

\* Exactly one of `query` or `query_embedding` is required.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from tool import run_tool

# Text query
result = run_tool(
    query="quarterly invoice",
    collection="documents",
    db_path="./chroma_db",
    n_results=3
)

# Pre-computed vector, with a metadata filter
result = run_tool(
    query_embedding=[0.12, 0.94, -0.31],
    collection="documents",
    where={"type": "finance"}
)
```

### Example output

```json
{
  "success": true,
  "data": {
    "collection": "documents",
    "query": "quarterly invoice",
    "distance_metric": "cosine",
    "collection_size": 4,
    "result_count": 2,
    "results": [
      {
        "rank": 1,
        "id": "d1",
        "document": "Invoice for Q3 services",
        "metadata": { "type": "finance" },
        "distance": 0.0,
        "similarity": 1.0
      },
      {
        "rank": 2,
        "id": "d3",
        "document": "Invoice addendum Q3",
        "metadata": { "type": "finance" },
        "distance": 0.001249,
        "similarity": 0.998751
      }
    ],
    "filters_applied": null
  }
}
```

### Error output

Errors are returned as data rather than raised, so a calling agent can read and act on them:

```json
{
  "success": false,
  "error": "Collection 'reports' was not found. Available collections: documents, embeddings."
}
```

## Notes

- **`similarity` is provided because Chroma returns distances, where lower is better.** A calling model reading a bare "score" will usually assume higher is better and rank results backwards. Both values are returned: `distance` is Chroma's raw output, `similarity` is normalised so higher is better. The metric used is reported as `distance_metric`, since the conversion differs between `cosine`, `ip` and `l2`.
- **Results are flattened.** Chroma returns parallel arrays nested one level deep (`ids[0]`, `documents[0]`, `distances[0]`) because it supports batch queries. This tool sends a single query and zips those arrays into one list of result objects, which is far easier for a model to consume than four arrays it must index in lockstep.
- **Use `query_embedding` when the collection was built with a custom embedding model.** Querying by text uses the collection's embedding function; if that differs from the model the vectors were created with, the result is a dimension error or silently poor matches. The dimension error is caught and explained rather than passed through raw.
- **An empty collection returns `success: true` with zero results**, not an error — having nothing to match against is a valid state, not a failure.

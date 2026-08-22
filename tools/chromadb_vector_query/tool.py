"""
ChromaDB Vector Store Query Tool

Runs read-only semantic similarity searches against a local (persistent) Chroma
vector database. Accepts either a text query or a pre-computed embedding vector,
and returns ranked matches with documents, metadata, raw distances and a
normalised similarity score.

Read-only by design: this tool never creates, modifies or deletes collections.
"""

import os
from typing import Any, Dict, List, Optional

# Chroma reports how "far apart" two vectors are. Lower is better, which is the
# opposite of what a calling model usually assumes when it sees a score, so each
# result also carries a similarity where higher is better.
_SUPPORTED_SPACES = ("cosine", "l2", "ip")


def _to_similarity(distance: float, space: str) -> float:
    """Converts a Chroma distance into a 'higher is better' similarity score."""
    try:
        if space in ("cosine", "ip"):
            # Both are returned as 1 - <similarity>, so this inverts cleanly.
            return round(1.0 - float(distance), 6)
        # l2 is a squared euclidean distance with no fixed upper bound;
        # 1/(1+d) maps it into (0, 1] while preserving ordering.
        return round(1.0 / (1.0 + float(distance)), 6)
    except (TypeError, ValueError):
        return 0.0


def _resolve_space(collection: Any) -> str:
    """
    Reads the distance metric a collection was built with (defaults to l2).

    Chroma exposes this in two places. The collection *configuration* is
    authoritative and is populated however the collection was created. The
    `hnsw:space` metadata key is only present when the caller passed it via
    `metadata=`; a collection created the documented way, with
    `configuration={"hnsw": {"space": "cosine"}}`, has `metadata = None`.
    Reading metadata alone therefore misreports such a collection as l2 and
    applies the wrong similarity conversion, so configuration is checked first.
    """
    try:
        config = getattr(collection, "configuration", None) or {}
        hnsw = config.get("hnsw") if hasattr(config, "get") else None
        if hnsw and hasattr(hnsw, "get"):
            space = str(hnsw.get("space", "")).lower()
            if space in _SUPPORTED_SPACES:
                return space
    except Exception:
        # Older Chroma releases do not expose `configuration`; fall through.
        pass

    metadata = getattr(collection, "metadata", None) or {}
    space = str(metadata.get("hnsw:space", "l2")).lower()
    return space if space in _SUPPORTED_SPACES else "l2"


def run_tool(
    query: str = "",
    collection: str = "",
    db_path: str = "./chroma_db",
    n_results: int = 5,
    query_embedding: Optional[List[float]] = None,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Queries a local Chroma collection for semantic similarity matches.

    Args:
        query (str): Natural-language search text. Embedded using the
            collection's own embedding function.
        collection (str): Name of the collection to search. Required.
        db_path (str): Path to the persistent Chroma directory.
        n_results (int): Number of matches to return (1-100).
        query_embedding (list[float], optional): Pre-computed vector. Use this
            instead of `query` when embeddings are generated elsewhere; it
            avoids loading any embedding model.
        where (dict, optional): Metadata filter, e.g. {"source": "docs"}.
        where_document (dict, optional): Document content filter,
            e.g. {"$contains": "invoice"}.

    Returns:
        Dict[str, Any]: {"success": True, "data": {...}} on success, or
        {"success": False, "error": "..."} with a readable explanation.
    """
    try:
        import chromadb
    except ImportError:
        return {
            "success": False,
            "error": "The 'chromadb' package is not installed. Install it with: pip install chromadb",
        }

    if not collection or not str(collection).strip():
        return {"success": False, "error": "Parameter 'collection' is required (the name of the collection to search)."}

    has_text = bool(query and str(query).strip())
    has_vector = query_embedding is not None and len(query_embedding) > 0

    if not has_text and not has_vector:
        return {"success": False, "error": "Provide either 'query' (search text) or 'query_embedding' (a pre-computed vector)."}

    if has_text and has_vector:
        return {"success": False, "error": "Provide only one of 'query' or 'query_embedding', not both."}

    try:
        limit = int(n_results)
    except (TypeError, ValueError):
        return {"success": False, "error": "Parameter 'n_results' must be an integer."}
    limit = max(1, min(limit, 100))

    resolved_path = os.path.abspath(os.path.expanduser(str(db_path)))
    if not os.path.isdir(resolved_path):
        return {
            "success": False,
            "error": f"No Chroma database directory found at '{resolved_path}'. Check 'db_path' points at an existing persistent store.",
        }

    # --- Connect -----------------------------------------------------------
    try:
        client = chromadb.PersistentClient(path=resolved_path)
    except Exception as exc:
        return {"success": False, "error": f"Could not open the Chroma database at '{resolved_path}': {exc}"}

    # --- Locate the collection --------------------------------------------
    try:
        target = client.get_collection(name=str(collection).strip())
    except Exception:
        try:
            available = sorted(c.name for c in client.list_collections())
        except Exception:
            available = []
        hint = f" Available collections: {', '.join(available)}." if available else " This database contains no collections."
        return {"success": False, "error": f"Collection '{collection}' was not found.{hint}"}

    space = _resolve_space(target)

    try:
        total = target.count()
    except Exception:
        total = None

    if total == 0:
        return {
            "success": True,
            "data": {
                "collection": str(collection).strip(),
                "query": query if has_text else "<embedding>",
                "distance_metric": space,
                "collection_size": 0,
                "result_count": 0,
                "results": [],
                "note": "The collection exists but contains no documents, so there is nothing to match against.",
            },
        }

    # --- Query -------------------------------------------------------------
    params: Dict[str, Any] = {
        "n_results": limit,
        "include": ["documents", "metadatas", "distances"],
    }
    if has_vector:
        params["query_embeddings"] = [list(query_embedding)]
    else:
        params["query_texts"] = [str(query).strip()]
    if where:
        params["where"] = where
    if where_document:
        params["where_document"] = where_document

    try:
        raw = target.query(**params)
    except Exception as exc:
        message = str(exc)
        lowered = message.lower()
        if "dimension" in lowered:
            return {
                "success": False,
                "error": (
                    f"Embedding dimension mismatch: {message} This usually means the collection was built with a "
                    "different embedding model than the one being used to embed the query. Pass a matching "
                    "'query_embedding' generated by the original model instead of using 'query'."
                ),
            }
        return {"success": False, "error": f"Query failed: {message}"}

    # Chroma returns parallel arrays nested one level per query. Only one query
    # is ever sent here, so unwrap [0] and zip the arrays into result objects.
    def _first(key: str) -> List[Any]:
        value = raw.get(key)
        if not value:
            return []
        return value[0] or []

    ids = _first("ids")
    documents = _first("documents")
    metadatas = _first("metadatas")
    distances = _first("distances")

    results = []
    for rank, doc_id in enumerate(ids):
        distance = distances[rank] if rank < len(distances) else None
        results.append(
            {
                "rank": rank + 1,
                "id": doc_id,
                "document": documents[rank] if rank < len(documents) else None,
                "metadata": metadatas[rank] if rank < len(metadatas) else None,
                "distance": round(float(distance), 6) if distance is not None else None,
                "similarity": _to_similarity(distance, space) if distance is not None else None,
            }
        )

    return {
        "success": True,
        "data": {
            "collection": str(collection).strip(),
            "query": query if has_text else "<embedding>",
            "distance_metric": space,
            "collection_size": total,
            "result_count": len(results),
            "results": results,
            "filters_applied": {"where": where, "where_document": where_document} if (where or where_document) else None,
        },
    }


if __name__ == "__main__":
    output = run_tool(
        query="semantic search example",
        collection="documents",
        db_path="./chroma_db",
        n_results=3,
    )
    print("Test execution output:", output)

"""
Google Gemini / Vertex AI embeddings tool for AI agents and MCP Hub.
Generates text embeddings for semantic search.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence

DEFAULT_MODEL = "models/text-embedding-004"
VALID_TASK_TYPES = {
    "retrieval_query",
    "retrieval_document",
    "semantic_similarity",
    "classification",
    "clustering",
}


def _normalize_texts(query: str = "", texts: Optional[Sequence[str]] = None) -> List[str]:
    if texts:
        return [str(t).strip() for t in texts if str(t).strip()]
    if query and str(query).strip():
        return [str(query).strip()]
    return []


def embed_texts(
    query: str = "",
    texts: Optional[Sequence[str]] = None,
    model: str = DEFAULT_MODEL,
    task_type: str = "retrieval_document",
    title: Optional[str] = None,
    provider: str = "gemini",
    api_key: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    contents = _normalize_texts(query=query, texts=texts)
    if not contents:
        return {
            "success": False,
            "error": "Provide a non-empty 'query' string or a 'texts' list.",
        }

    task_type = str(task_type or "retrieval_document").strip().lower()
    if task_type not in VALID_TASK_TYPES:
        return {
            "success": False,
            "error": f"Invalid task_type. Use one of: {', '.join(sorted(VALID_TASK_TYPES))}.",
        }

    provider = str(provider or "gemini").strip().lower()
    if provider not in {"gemini", "vertex"}:
        return {
            "success": False,
            "error": "Parameter 'provider' must be 'gemini' or 'vertex'.",
        }

    try:
        import google.generativeai as genai
    except ImportError:
        return {
            "success": False,
            "error": "Missing dependency. Run: pip install -r requirements.txt",
        }

    try:
        model_name = model if str(model).startswith("models/") else f"models/{model}"

        if provider == "vertex":
            project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT")
            if not project:
                return {
                    "success": False,
                    "error": "Vertex AI requires GOOGLE_CLOUD_PROJECT (and optional GOOGLE_CLOUD_LOCATION).",
                }
            location = (
                os.getenv("GOOGLE_CLOUD_LOCATION")
                or os.getenv("GOOGLE_CLOUD_REGION")
                or "us-central1"
            )
            genai.configure(
                transport="rest",
                client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"},
            )
        else:
            token = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not token:
                return {
                    "success": False,
                    "error": "Gemini API key is required. Pass api_key or set GOOGLE_API_KEY / GEMINI_API_KEY.",
                }
            genai.configure(api_key=token)

        embeddings: List[List[float]] = []
        for i, text in enumerate(contents):
            request: Dict[str, Any] = {
                "model": model_name,
                "content": text,
                "task_type": task_type,
            }
            if title and task_type == "retrieval_document" and i == 0:
                request["title"] = title

            result = genai.embed_content(**request)
            vector = result.get("embedding") if isinstance(result, dict) else getattr(result, "embedding", None)
            if not vector:
                return {
                    "success": False,
                    "error": "The embeddings API returned an empty vector.",
                }
            embeddings.append(list(vector))

        return {
            "success": True,
            "data": {
                "provider": provider,
                "model": model_name,
                "task_type": task_type,
                "count": len(embeddings),
                "dimensions": len(embeddings[0]) if embeddings else 0,
                "embeddings": embeddings,
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate embeddings: {str(e)}",
        }


def run_tool(query: str = "", **kwargs: Any) -> Dict[str, Any]:
    """Standard agent dispatcher entrypoint."""
    return embed_texts(
        query=kwargs.get("query") or query,
        texts=kwargs.get("texts"),
        model=kwargs.get("model", DEFAULT_MODEL),
        task_type=kwargs.get("task_type", "retrieval_document"),
        title=kwargs.get("title"),
        provider=kwargs.get("provider", "gemini"),
        api_key=kwargs.get("api_key"),
    )


if __name__ == "__main__":
    print(run_tool("semantic search with Gemini embeddings"))

"""Embedding provider integration (Phase 4).

Keeps external/ML embedding model access inside app/integrations/ per
.md/07_Backend_Structure.md section 9.
"""
import asyncio
from functools import lru_cache

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def _get_model():
    """Load and cache the SentenceTransformer model once per process."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBEDDING_MODEL_ID)


def _encode_sync(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    vectors = model.encode(texts, convert_to_numpy=True)
    return [vec.tolist() for vec in vectors]


async def generate_embedding(text: str) -> list[float]:
    """Generate a single normalized embedding vector for text."""
    results = await generate_embeddings_batch([text])
    return results[0]


async def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a batch of texts off the event loop."""
    if not texts:
        return []
    try:
        return await asyncio.to_thread(_encode_sync, texts)
    except Exception as exc:
        raise RuntimeError(f"Embedding generation failed: {exc}") from exc

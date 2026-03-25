import logging
from fastembed import TextEmbedding
from govai.config import settings

logger = logging.getLogger(__name__)

_embedding_model: TextEmbedding | None = None

from fastapi.concurrency import run_in_threadpool

def get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=settings.embedding_model)
    return _embedding_model

def _generate_embedding_sync(text: str) -> list[float]:
    model = get_embedding_model()
    # FastEmbed returns a generator of numpy arrays
    embeddings_generator = model.embed([text])
    embedding_array = next(embeddings_generator)
    return embedding_array.tolist()

async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text using a thread pool."""
    try:
        return await run_in_threadpool(_generate_embedding_sync, text)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise

import logging
from fastembed import TextEmbedding
from govai.config import settings

logger = logging.getLogger(__name__)

_embedding_model: TextEmbedding | None = None

def get_embedding_model() -> TextEmbedding:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding(model_name=settings.embedding_model)
    return _embedding_model

async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text."""
    try:
        model = get_embedding_model()
        # FastEmbed returns a generator of numpy arrays, we want the first array converted to a list of floats
        embeddings_generator = model.embed([text])
        embedding_array = next(embeddings_generator)
        return embedding_array.tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise

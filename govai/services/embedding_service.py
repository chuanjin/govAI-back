import logging
import unicodedata
from fastembed import TextEmbedding
from govai.config import settings

logger = logging.getLogger(__name__)

_embedding_model: TextEmbedding | None = None
_resolved_embedding_model_name: str | None = None

from fastapi.concurrency import run_in_threadpool

def get_embedding_model() -> TextEmbedding:
    global _embedding_model
    global _resolved_embedding_model_name
    if _embedding_model is None:
        supported_models = {
            model.get("model")
            for model in TextEmbedding.list_supported_models()
            if model.get("model")
        }

        selected_model = settings.embedding_model
        if selected_model not in supported_models:
            fallback_model = "intfloat/multilingual-e5-large"
            logger.warning(
                "Embedding model '%s' is not supported by this fastembed build. "
                "Falling back to '%s'.",
                selected_model,
                fallback_model,
            )
            selected_model = fallback_model

        _resolved_embedding_model_name = selected_model
        _embedding_model = TextEmbedding(model_name=selected_model)

    if _resolved_embedding_model_name and _resolved_embedding_model_name != settings.embedding_model:
        logger.debug(
            "Configured embedding model '%s' overridden to '%s'.",
            settings.embedding_model,
            _resolved_embedding_model_name,
        )
    return _embedding_model

def _generate_embedding_sync(text: str) -> list[float]:
    normalized_text = unicodedata.normalize("NFKC", text).strip()
    if not normalized_text:
        raise ValueError("Cannot generate embedding for empty text")

    model = get_embedding_model()
    # FastEmbed returns a generator of numpy arrays
    embeddings_generator = model.embed([normalized_text])
    embedding_array = next(embeddings_generator)
    return embedding_array.tolist()

async def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for the given text using a thread pool."""
    try:
        return await run_in_threadpool(_generate_embedding_sync, text)
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise

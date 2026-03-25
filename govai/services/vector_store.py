import logging
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    ScalarQuantization,
    ScalarType,
    ScalarQuantizationConfig,
)
from govai.config import settings

logger = logging.getLogger(__name__)

_async_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Sync client for startup/seeding."""
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
    )


async def get_async_qdrant_client() -> AsyncQdrantClient:
    global _async_client
    if _async_client is not None:
        return _async_client

    try:
        if settings.qdrant_api_key:
            logger.info(f"Connecting to Cloud Qdrant at {settings.qdrant_url}")
        else:
            logger.info(f"Connecting to Local Qdrant at {settings.qdrant_url}")

        _async_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )
        # Test connectivity
        await _async_client.get_collections()
        logger.info(f"✅ Successfully connected to Qdrant (Async)")
        return _async_client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant at {settings.qdrant_url}: {e}")
        # Return a client instance anyway to avoid crashes
        return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


def ensure_collection():
    """Create the collection if it doesn't exist with optimized search settings."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(
                    type=ScalarType.INT8,
                    always_ram=True,
                ),
            ),
        )
        logger.info(f"Created collection with Scalar Quantization: {settings.qdrant_collection}")
    else:
        logger.info(f"Collection already exists: {settings.qdrant_collection}")


def delete_collection():
    """Delete the collection if it exists."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection in collections:
        client.delete_collection(settings.qdrant_collection)
        logger.info(f"Deleted collection: {settings.qdrant_collection}")
    else:
        logger.info(f"Collection NOT found: {settings.qdrant_collection}")


def upsert_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """Upsert document chunks with their embeddings into Qdrant."""
    client = get_qdrant_client()
    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=chunk.get("id", i),
                vector=embedding,
                payload={
                    "content": chunk["content"],
                    "title": chunk.get("title", ""),
                    "source_url": chunk.get("source_url", ""),
                    "section": chunk.get("section", ""),
                    "language": chunk.get("language", "en"),
                },
            )
        )
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
    )
    logger.info(f"Upserted {len(points)} chunks into Qdrant")


async def search_similar(
    query_embedding: list[float],
    top_k: int | None = None,
    language_filter: str | None = None,
) -> list[dict]:
    """Search for similar document chunks using async client."""
    client = await get_async_qdrant_client()
    k = top_k or settings.top_k

    results = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=k,
    )

    chunks = []
    for point in results.points:
        chunks.append(
            {
                "content": point.payload.get("content", ""),
                "title": point.payload.get("title", ""),
                "source_url": point.payload.get("source_url", ""),
                "section": point.payload.get("section", ""),
                "score": point.score,
            }
        )
    return chunks

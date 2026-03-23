import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
)
from govai.config import settings

logger = logging.getLogger(__name__)

_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
    return _client


def ensure_collection():
    """Create the collection if it doesn't exist."""
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in collections:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"Created collection: {settings.qdrant_collection}")
    else:
        logger.info(f"Collection already exists: {settings.qdrant_collection}")


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
    """Search for similar document chunks."""
    client = get_qdrant_client()
    k = top_k or settings.top_k

    search_params = {
        "collection_name": settings.qdrant_collection,
        "query_vector": query_embedding,
        "limit": k,
    }

    results = client.query_points(
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

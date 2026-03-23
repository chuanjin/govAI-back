import logging
from govai.services.embedding_service import generate_embedding
from govai.services.vector_store import search_similar
from govai.services.prompt_builder import build_rag_prompt

logger = logging.getLogger(__name__)


async def retrieve_and_build_context(
    query: str,
    top_k: int = 5,
    language: str | None = None,
) -> tuple[str, list[dict]]:
    """
    Full RAG pipeline:
    1. Generate embedding for user query
    2. Search vector store for relevant chunks
    3. Build augmented prompt with retrieved context

    Returns (augmented_prompt, retrieved_chunks)
    """
    # Step 1: Embed the query
    logger.info(f"Generating embedding for query: {query[:80]}...")
    query_embedding = await generate_embedding(query)

    # Step 2: Search for similar chunks
    logger.info(f"Searching for top-{top_k} relevant chunks...")
    chunks = await search_similar(
        query_embedding=query_embedding,
        top_k=top_k,
        language_filter=language,
    )
    logger.info(f"Retrieved {len(chunks)} chunks")

    # Step 3: Build augmented prompt
    augmented_prompt = build_rag_prompt(chunks, query)

    return augmented_prompt, chunks

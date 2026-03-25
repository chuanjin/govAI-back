import logging
from fastapi import APIRouter, HTTPException
from govai.models.schemas import (
    ChatRequest,
    ChatResponse,
    StructuredAnswer,
    Source,
    GuidanceStep,
)
from govai.services.session_manager import session_manager
from govai.services.rag_service import retrieve_and_build_context
from govai.services.llm_service import generate_answer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

GUIDANCE_TRIGGERS = [
    "guide me",
    "step by step",
    "walk me through",
    "help me do",
    "how do i do",
    "vägled mig",
    "steg för steg",
    "指导我",
    "一步一步",
]


def detect_guidance_mode(message: str) -> bool:
    """Detect if user wants step-by-step guidance."""
    lower = message.lower()
    return any(trigger in lower for trigger in GUIDANCE_TRIGGERS)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint — processes user messages through RAG + LLM."""
    try:
        # Get or create session
        session_id = session_manager.get_or_create_session(request.session_id)

        # Detect guidance mode
        is_guidance = detect_guidance_mode(request.message)

        # Add user message to history
        session_manager.add_message(session_id, "user", request.message)

        # RAG: retrieve relevant context
        augmented_prompt, retrieved_chunks = await retrieve_and_build_context(
            query=request.message,
            language=request.language,
        )

        # Get conversation history
        history = session_manager.get_history(session_id)

        # Generate answer via LLM
        raw_answer = await generate_answer(
            augmented_prompt=augmented_prompt,
            conversation_history=history[:-1],  # Exclude current msg (in prompt)
            is_guidance_mode=is_guidance,
            language=request.language,
        )

        # Build structured response
        sources = [
            Source(title=s.get("title", ""), url=s.get("url", ""))
            for s in raw_answer.get("sources", [])
        ]

        answer = StructuredAnswer(
            summary=raw_answer.get("summary", ""),
            eligibility=raw_answer.get("eligibility"),
            steps=raw_answer.get("steps", []),
            notes=raw_answer.get("notes"),
            sources=sources,
        )

        # Build guidance step if applicable
        guidance_step = None
        if is_guidance and raw_answer.get("guidance_question"):
            guidance_step = GuidanceStep(
                step_number=1,
                question=raw_answer["guidance_question"],
                options=raw_answer.get("guidance_options", []),
            )

        # Save assistant response to history
        session_manager.add_message(
            session_id, "assistant", raw_answer.get("summary", "")
        )

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            is_guidance_mode=is_guidance,
            guidance_step=guidance_step,
        )

    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your request. Please try again.",
        )

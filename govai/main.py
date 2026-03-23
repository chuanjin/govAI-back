import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from govai.routers.chat import router as chat_router
from govai.models.schemas import HealthResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 GovAssist AI Backend starting up...")
    # Try to connect to Qdrant on startup (non-blocking)
    try:
        from govai.services.vector_store import ensure_collection
        ensure_collection()
        logger.info("✅ Qdrant connection established")
    except Exception as e:
        logger.warning(f"⚠️  Qdrant not available: {e}. RAG will fail until Qdrant is running.")
    yield
    logger.info("👋 GovAssist AI Backend shutting down...")


app = FastAPI(
    title="GovAssist AI",
    description="AI-powered Swedish government service assistant",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat_router)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()

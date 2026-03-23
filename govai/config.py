from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openrouter_api_key: str = ""
    openrouter_api_base: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "openrouter/auto"

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimensions: int = 384

    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "gov_documents"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5

    max_context_messages: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

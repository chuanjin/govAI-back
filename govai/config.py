from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    gemini_api_key: str = ""
    primary_model: str = "gemini/gemini-2.0-flash"
    fallback_model: str = "gemini/gemini-2.5-flash"

    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_dimensions: int = 1024

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""
    qdrant_collection: str = "gov_documents"

    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5

    max_context_messages: int = 10

    cors_origins: list[str] | str = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()

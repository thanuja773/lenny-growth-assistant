import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/lenny_growth_assistant"
    FRONTEND_URL: str = "http://localhost:3000"
    
    # LLM configurations
    LLM_PROVIDER: Optional[str] = "ollama"
    LLM_FALLBACK_PROVIDER: Optional[str] = None
    LLM_TIMEOUT_SECONDS: int = 60
    
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    
    # Ingestion configurations
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Retrieval configurations
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MAX_TOP_K: int = 20
    RETRIEVAL_MIN_SIMILARITY: float = 0.30
    RETRIEVAL_CANDIDATE_POOL_SIZE: int = 15

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env"))),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

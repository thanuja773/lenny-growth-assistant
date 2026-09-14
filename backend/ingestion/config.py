import os
from pydantic_settings import BaseSettings

class IngestionSettings(BaseSettings):
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 700
    CHUNK_OVERLAP: int = 100
    GITHUB_REPO: str = "ChatPRD/lennys-podcast-transcripts"
    DATA_DIR: str = os.getenv("DATA_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw")))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/lenny_growth_assistant")

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "extra": "ignore"}

settings = IngestionSettings()

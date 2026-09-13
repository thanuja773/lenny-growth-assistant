from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    DATABASE_URL: str
    
    # LLM configurations placeholders
    LLM_PROVIDER: Optional[str] = "ollama"
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()\n
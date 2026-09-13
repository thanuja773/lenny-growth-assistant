import os

dirs = [
    "data/raw",
    "backend/app/core",
    "backend/app/api",
    "backend/app/db/models",
    "backend/app/services",
    "backend/tests",
    "backend/alembic/versions"
]

inits = [
    "backend/app/__init__.py",
    "backend/app/core/__init__.py",
    "backend/app/api/__init__.py",
    "backend/app/db/__init__.py",
    "backend/app/services/__init__.py",
    "backend/tests/__init__.py"
]

files = {
    "docker-compose.yml": """
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
      POSTGRES_DB: ${POSTGRES_DB:-lenny_growth_assistant}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d lenny_growth_assistant"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
    driver: local
""",
    ".env.example": """
APP_ENV=development
LOG_LEVEL=INFO

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=lenny_growth_assistant
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
""",
    ".env": """
APP_ENV=development
LOG_LEVEL=INFO

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=lenny_growth_assistant
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/lenny_growth_assistant
""",
    "backend/pyproject.toml": """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "lenny-assistant-backend"
version = "0.1.0"
description = "FastAPI backend for Lenny Growth Assistant"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn>=0.30.0",
    "sqlalchemy>=2.0.30",
    "psycopg[binary]>=3.1.18",
    "alembic>=1.13.1",
    "pgvector>=0.2.5",
    "pydantic>=2.7.4",
    "pydantic-settings>=2.3.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.2.2",
    "httpx>=0.27.0",
]

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
""",
    "backend/app/core/config.py": """
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

settings = Settings()
""",
    "backend/app/core/logging.py": """
import logging
from app.core.config import settings

def setup_logging():
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("lenny_assistant")
    return logger

logger = setup_logging()
""",
    "backend/app/db/session.py": """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "backend/app/db/base.py": """
from sqlalchemy.orm import declarative_base

Base = declarative_base()
""",
    "backend/app/db/models/user.py": """
import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "backend/app/db/models/session.py": """
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
""",
    "backend/app/db/models/message.py": """
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False) # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session")
""",
    "backend/app/db/models/transcript.py": """
import uuid
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    source_url = Column(String(1024), nullable=True)
    source_type = Column(String(50), nullable=False) # 'podcast', 'newsletter'
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
""",
    "backend/app/db/models/transcript_chunk.py": """
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base

EMBEDDING_DIM = 1536 # Example dimension for typical OpenAI embeddings; can be configurable

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIM))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transcript = relationship("Transcript")
""",
    "backend/app/db/models/artifact.py": """
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False, index=True)
    artifact_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    session = relationship("Session")
""",
    "backend/app/db/models/__init__.py": """
from app.db.models.user import User
from app.db.models.session import Session
from app.db.models.message import Message
from app.db.models.transcript import Transcript
from app.db.models.transcript_chunk import TranscriptChunk
from app.db.models.artifact import Artifact
""",
    "backend/app/api/health.py": """
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
import logging

router = APIRouter()
logger = logging.getLogger("lenny_assistant.health")

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to check db connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )
""",
    "backend/app/api/router.py": """
from fastapi import APIRouter
from app.api import health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
""",
    "backend/app/main.py": """
from fastapi import FastAPI
from app.api.router import api_router
from app.core.logging import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title="Lenny Growth Assistant API",
        version="0.1.0",
        description="Backend API for Lenny Growth Assistant"
    )

    app.include_router(api_router)

    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting up Lenny Growth Assistant API")

    return app

app = create_app()
""",
    "backend/tests/test_health.py": """
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_db_connected():
    response = client.get("/health")
    assert response.status_code in [200, 503]

def test_health_check_db_unavailable():
    from app.db.session import get_db
    def override_get_db():
        raise Exception("Mock DB Failure")
    
    app.dependency_overrides[get_db] = override_get_db
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database connection failed"
    app.dependency_overrides.clear()
""",
    "backend/tests/test_db.py": """
from sqlalchemy import create_engine
from app.db.base import Base
from app.db.models import *

def test_models_importable():
    # If this runs, models are successfully imported and configured
    assert len(Base.metadata.tables) > 0
""",
    "backend/alembic.ini": """
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+psycopg://postgres:postgres@localhost:5432/lenny_growth_assistant

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""",
    "backend/alembic/env.py": """
import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy import text
from alembic import context
import os

from app.db.base import Base
import app.db.models  # to ensure all models are loaded

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Load DATABASE_URL from environment if available
db_url = os.environ.get("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            # Enable pgvector if not enabled
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""",
    "backend/README.md": """
# Backend for Lenny Growth Assistant

## Purpose
The FastAPI backend serves as the orchestration layer for the Lenny Growth Assistant. It connects the frontend with the LLM (Ollama or Cloud) and the PostgreSQL pgvector database for RAG (Retrieval-Augmented Generation).

## Architecture
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector (via SQLAlchemy & async Psycopg if needed, currently sync)
- **Dependency Management**: uv
- **Migrations**: Alembic

## Prerequisites
- Docker & Docker Compose
- `uv` (Python package manager)
- Python 3.11+

## Setup Instructions

1. **Install dependencies using uv:**
   ```bash
   cd backend
   uv venv
   # on windows: .venv\Scripts\activate
   uv pip install -e .[dev]
   ```

2. **Environment Variables:**
   Copy `.env.example` from the root into the root directory as `.env` and configure accordingly.

3. **Start PostgreSQL:**
   From the project root:
   ```bash
   docker-compose up -d
   ```

4. **Run Migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

5. **Start FastAPI:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Endpoints
- **Health Check**: `GET http://localhost:8000/health`
- **API Docs**: `GET http://localhost:8000/docs`

## Testing
Run pytest:
```bash
cd backend
pytest
```

## Troubleshooting
- If DB connection fails, ensure Docker Compose is running and `DATABASE_URL` in `.env` is correct.
"""
}

def write_files():
    for d in dirs:
        os.makedirs(os.path.join(r"c:\lenny-growth-assisstant", d.replace('/', '\\')), exist_ok=True)
    
    for i in inits:
        full_path = os.path.join(r"c:\lenny-growth-assisstant", i.replace('/', '\\'))
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("")

    for filepath, content in files.items():
        full_path = os.path.join(r"c:\lenny-growth-assisstant", filepath.replace('/', '\\'))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        # Using simple \n mapping
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

if __name__ == "__main__":
    write_files()

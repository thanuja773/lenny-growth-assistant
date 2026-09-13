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
   # on windows: .venv\Scriptsctivate
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
- If DB connection fails, ensure Docker Compose is running and `DATABASE_URL` in `.env` is correct.\n
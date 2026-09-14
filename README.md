# Lenny Growth Assistant

A production-quality AI product-intelligence workspace built on top of FastAPI, PostgreSQL (pgvector), and Next.js. 

This repository contains the complete implementation up through Step 9, fulfilling all evaluator requirements including Docker containerization, resilient architecture, strict security/hardening protocols, and a Ship 30 for 30 artifact generator.

## Prerequisites
- Git
- Docker & Docker Compose
- [Ollama](https://ollama.com/) (installed locally on host)
- Llama 3 model for Ollama
- (Optional) Python 3.10 and Node 20 if running outside Docker

## Quick Start (Evaluator Setup)

### 1. Clone & Configuration
Clone this repository. Then copy the `.env.example` into a `.env` file at the root:
```bash
cp .env.example .env
```
Ensure `OLLAMA_BASE_URL` is set to `http://host.docker.internal:11434` for Docker Desktop environments. 

### 2. Prepare Local Ollama
Ollama is strictly designed to run natively on the host machine to utilize local GPU/CPU hardware. 
```bash
ollama pull llama3
ollama run llama3
```
Ensure the Ollama API is available on the host (usually port `11434`).

### 3. Start Application Infrastructure
Launch the database, backend, and frontend via Docker Compose:
```bash
docker compose up --build -d
```
The backend explicitly waits for the database to pass a `pg_isready` healthcheck before initializing.

### 4. Database Migrations
Initialize the database schemas using Alembic on the backend container:
```bash
docker compose exec backend uv run alembic upgrade head
```

### 5. Data Ingestion (One-Time)
To seed the database with transcript data and embeddings (do this once):
```bash
docker compose exec backend uv run python -m ingestion.__main__
```

### 6. Verify Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Healthcheck**: http://localhost:8000/health
- **Backend API Docs**: http://localhost:8000/docs

## Troubleshooting

- **Ollama Timeout / Connection Error**: If the backend Docker container cannot reach Ollama, verify `host.docker.internal` is mapped properly on your OS, or explicitly set `OLLAMA_BASE_URL` in `.env` to your machine's LAN IP address.
- **Port Conflicts**: If `5432`, `8000`, or `3000` are blocked, either stop the conflicting service on your host or change the exposed port mapping in `docker-compose.yml`.
- **Database Connection Failure**: If the backend is looping or returning 503s, run `docker compose logs db` to ensure PostgreSQL initialized correctly and the volume isn't locked.
- **Anthropic Features**: If you switch to the Anthropic provider without adding an `ANTHROPIC_API_KEY` to `.env`, the API will return a configuration warning and cleanly fail.

## Non-Docker Development Compatibility
The application retains full backward compatibility for local development without Docker:
- `db`: You must run a pgvector database (or use `docker compose up db -d`).
- `backend`: `cd backend && uv run uvicorn app.main:app --reload`
- `frontend`: `cd frontend && npm run dev`
*(Ensure you update `.env` `DATABASE_URL` to `localhost` and `OLLAMA_BASE_URL` to `127.0.0.1`)*

## Features Included
- **Persistent Multi-Turn RAG Agent**: Session state stored securely in Postgres.
- **Provider Abstraction**: Switch between local Ollama and Anthropic instantly.
- **Artifact Generation**: End-to-end Ship 30 essay generation.
- **Security & Resilience**: Request ID telemetry, strict AST markdown rendering (no HTML injection), strict input payload validation, XML-tagged prompt injection defense, and graceful 503 exception handling on subsystem failures.

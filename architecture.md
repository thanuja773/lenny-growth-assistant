# Architecture & Technical Principles

## Core Principles
- **Separation of Concerns**: Clear boundary between frontend (UI/UX) and backend (RAG/LLM logic).
- **Provider Abstraction**: LLM calls must go through an interface supporting both Ollama (local) and cloud providers.
- **Retrieval Isolation**: Retrieval logic (fetching from pgvector) is isolated from text generation.
- **Explicit Tool Boundaries**: Agent tools have well-defined, single-purpose responsibilities.
- **Configuration Driven**: All configurations via environment variables (`.env`). No committed secrets.
- **Observability**: Structured logs and structured errors.

## High-Level Architecture
1. **Frontend (Next.js)**: Handles user interaction, chat state, and secure artifact rendering.
2. **Backend (FastAPI)**: REST/WebSocket API, agent orchestration, prompt construction, LLM interaction.
3. **Database (PostgreSQL + pgvector)**: Stores transcripts (chunks, embeddings), conversations, and artifacts.
4. **Ingestion Pipeline**: Python scripts to parse transcripts, chunk them, embed them, and load them into PostgreSQL.

## Data Flow (Q&A)
1. User submits question via Next.js UI.
2. FastAPI receives the request and extracts conversation history.
3. Backend converts the question to an embedding vector.
4. Backend queries PostgreSQL (pgvector) for most similar transcript chunks.
5. Backend constructs a prompt with context + history + question.
6. LLM (Ollama or Cloud) generates the response.
7. Backend streams/returns the response and citations to the frontend.

# Lenny Growth Assistant - Architecture Document

## System Architecture

The Lenny Growth Assistant is structured into clean, decoupled layers to maintain modularity, testability, and resilience.

```
┌────────────────────────────────────────────────────────┐
│               Client / Frontend Layer                  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                     │
│  ┌────────────────────┐      ┌──────────────────────┐  │
│  │   /health Route    │      │ /api/retrieval/search│  │
│  └────────────────────┘      └──────────┬───────────┘  │
│                                         │              │
│                              ┌──────────▼───────────┐  │
│                              │   RetrievalService   │  │
│                              └─────┬──────────┬─────┘  │
│                                    │          │        │
│                ┌───────────────────┘          └─────┐  │
│                │                                    │  │
│       ┌────────▼─────────┐                 ┌────────▼┐ │
│       │  QueryEmbedder   │                 │Diversity│ │
│       │ (Local MiniLM)   │                 │ Filter  │ │
│       └──────────────────┘                 └─────────┘ │
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy (pgvector)
┌───────────────────────────▼────────────────────────────┐
│         PostgreSQL 16 + pgvector (Docker)              │
│  - transcripts (metadata, source_url)                  │
│  - transcript_chunks (content, embedding vector(384))  │
└────────────────────────────────────────────────────────┘
```

## Decoupled Pipeline Stages

1. **Step 1 - Foundation & Backend Setup**:
   - Containerized PostgreSQL with pgvector extension.
   - Core FastAPI application with SQLAlchemy ORM models (`transcripts`, `transcript_chunks`, `sessions`, `messages`, `artifacts`, `users`).
   - Alembic database migration chain.

2. **Step 2 - Transcript Ingestion Pipeline**:
   - Downloads transcripts from Lenny's podcast transcript repository.
   - Cleans formatting while preserving speaker turns and timestamps.
   - Chunks text into ~700-token sections with 100-token overlap.
   - Computes 384-dimensional embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
   - Persists data idempotently into PostgreSQL keyed by `source_url`.

3. **Step 3 - Semantic RAG Retrieval Layer**:
   - Encapsulates query embedding, pgvector cosine distance calculation, candidate oversampling, similarity thresholding, and lightweight diversity filtering.
   - Decoupled completely from LLM generation (Step 4) and agent routing (Step 5).
   - Zero external cloud dependencies or API keys required.
   - Returns rich metadata (`source_url`, `chunk_index`, `transcript_title`, `similarity_score`) for source traceability and citation grounding.

4. **Step 4 - LLM Provider & Grounding Layer (Current)**:
   - Implements a provider-independent LLM layer (`LLMProvider` protocol) supporting Ollama (local) and Anthropic (cloud).
   - Implements `POST /api/chat` for answering queries using a strict grounding prompt.
   - Protects against hallucination by returning a deterministic "Insufficient evidence" message if retrieval returns zero results.
   - Supports graceful provider fallback and rich source citation traceability.

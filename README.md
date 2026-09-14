# Lenny Growth Assistant

A production-quality AI product-intelligence workspace built on top of FastAPI, PostgreSQL (pgvector), and Next.js.

## Components
1. **Backend**: FastAPI with PostgreSQL and pgvector for RAG. Supports local Ollama (llama3) and Anthropic (claude-3).
2. **Frontend**: Next.js App Router with Tailwind CSS, Lucide Icons, and React Markdown.

## Startup Instructions

### 1. Backend
Ensure Docker (PostgreSQL) is running, then:
```bash
uv run uvicorn backend.app.main:app --reload
```
Runs at `http://127.0.0.1:8000`

### 2. Frontend
In the `frontend` directory:
```bash
npm run dev
```
Runs at `http://localhost:3000`

## Features
- Multi-turn conversation persistence (Sessions via PostgreSQL).
- Real-time provider toggling (Ollama / Anthropic).
- Grounded generation strictly using Lenny's transcript chunks.
- Insights panel showing source traceability.
- Artifact Generation: Convert conversations into Ship 30 for 30 essays.
- Secure Artifact Viewer: Built-in safe markdown AST parsing blocks arbitrary HTML/XSS.
- Secure markdown rendering (HTML sanitized).

# Lenny Growth Assistant

## Project Overview
A full-stack AI-powered conversational web application designed to answer product and growth questions using Lenny's Podcast and Newsletter transcripts as its knowledge base. It provides source-grounded answers, avoids hallucination, and supports advanced features like turning insights into Ship 30 for 30-style essays.

## Planned Architecture
- **Frontend**: Next.js, TypeScript, Tailwind CSS, shadcn/ui.
- **Backend**: Python, FastAPI, Pydantic.
- **Database**: PostgreSQL with pgvector for vector similarity search.
- **AI/LLM**: Local-first with Ollama, extensible to cloud providers (OpenAI, Anthropic).
- **Infrastructure**: Docker Compose for reproducible local environments.

## Technology Stack
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python), Pydantic
- **Data Persistence**: PostgreSQL, pgvector
- **LLM/Agent**: Ollama (local), abstracted cloud provider interface
- **Deployment & Ops**: Docker Compose, pytest

## Development Phases
1. **Phase 1: Project Foundation** (Current) - Monorepo setup, architectural documentation, and placeholder structure.
2. **Phase 2: Database & Ingestion** - Setup PostgreSQL + pgvector, create ingestion scripts for transcripts, and implement vector search.
3. **Phase 3: Backend & LLM Integration** - Build FastAPI endpoints, configure Ollama/Cloud LLMs, implement RAG pipeline, and basic agent tool boundaries.
4. **Phase 4: Frontend Chat Interface** - Build Next.js UI (chat area, sidebar, information panel).
5. **Phase 5: Artifacts & Advanced Features** - Ship 30 for 30 essay generation, in-app artifact viewer with secure HTML rendering.
6. **Phase 6: Testing & Refinement** - Add tests, refine UI/UX, and finalize documentation.

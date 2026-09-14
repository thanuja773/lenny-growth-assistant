# LLM Generation Service

The LLM generation service (Step 4) handles provider-independent response generation, incorporating transcript retrieval context via a strict grounding prompt.

## Providers

1. **Ollama** (Local): Default, uses the configured `OLLAMA_BASE_URL` (default `http://localhost:11434`) and `OLLAMA_MODEL` (default `llama3`).
2. **Anthropic** (Cloud): Requires `ANTHROPIC_API_KEY` and uses `ANTHROPIC_MODEL` (default `claude-3-haiku-20240307`).

## Fallback

Set `LLM_FALLBACK_PROVIDER` to another provider (e.g. `anthropic`) to automatically fail over if the primary `LLM_PROVIDER` fails (e.g. connection refused, timeout).

## Context & Grounding

The service executes vector search against pgvector, extracting source metadata (transcript title, URL, similarity score). The LLM is given strict system instructions to cite sources and avoid inventing facts. If retrieval returns 0 results above threshold, the service deterministic returns an "Insufficient evidence" message and does not query the LLM, avoiding hallucination.

# Agent Architecture

This directory contains the Agent Orchestrator for the Lenny Growth Assistant.

## Overview
The Growth Agent transforms the system from a single-turn question-answering pipeline into a multi-turn, stateful conversational agent that can reason about which tools to use. It satisfies the requirement for persistent sessions, explicit agent tools (transcript search and Ship 30 for 30 generation), and provider-aware execution.

## Components

### 1. `agent.py` (GrowthAgent)
The main orchestrator. When it receives a request:
1. It resolves or creates a PostgreSQL-persisted Session via `SessionManager`.
2. It constructs an `AgentState`.
3. It decides which tools to invoke based on the configured provider:
   - **Anthropic Provider**: Uses the official Anthropic Claude SDK with its native `tools` API (function calling) to intelligently decide when to use `search_transcripts` or `generate_ship30`.
   - **Ollama Provider**: Uses deterministic heuristic routing (regex checking for "Ship 30") because Ollama local models don't currently share the same proprietary native tools API layer in this system.
4. It persists both the user's message and the assistant's final generated answer.

### 2. Tools (`tools/`)
The tools are isolated action spaces the agent can call:
- **`search_transcripts.py`**: Wraps the existing semantic `RetrievalService`. It protects the underlying vector database search logic and exposes it as a clean tool returning structured sources.
- **`generate_ship30.py`**: A specialized content generation tool that accepts transcript chunks as context and forces the LLM to output a ~1,250-word grounded essay in the style of Ship 30 for 30.

### 3. Session & State Management
- **`session_manager.py`**: Encapsulates all CRUD logic for interacting with the `sessions` and `messages` tables via SQLAlchemy, abstracting PostgreSQL from the Agent logic.
- **`state.py`**: The ephemereal memory structure tracking the current request, recent history, retrieved context, and the tool trace.

## Grounding & Safety
The Agent heavily relies on strict grounding rules:
1. It treats transcript data as untrusted reference material.
2. If `search_transcripts` returns nothing, the agent forces an "Insufficient evidence" short-circuit to prevent hallucination, bypassing normal generation.
3. It preserves `SourceCitation` records all the way to the frontend for UI traceability.

## SDK Tradeoffs
To satisfy the assessment requirement ("Agent layer using Anthropic Claude Agent SDK"), the system integrates the Anthropic Python SDK specifically for its tool-calling capabilities. However, because the system MUST support local-only `Ollama` execution without an Anthropic API key, the logic strictly separates `_execute_anthropic_sdk` from `_execute_ollama_deterministic`. 

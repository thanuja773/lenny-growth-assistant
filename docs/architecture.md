# Frontend Architecture

The frontend is a Next.js (App Router) application.

## 1. Page Structure
- `app/page.tsx`: The main orchestrator holding React state (session, messages, provider).
- `app/layout.tsx`: Root layout with Geist font definitions and metadata.
- `app/globals.css`: Tailwind configuration and premium dark-mode theme variables.

## 2. Component Structure
- **Layout**: `Sidebar`, `Topbar`, `InsightsPanel`
- **Chat**: `ChatArea` (Markdown), `Composer`, `EmptyState`
- **Sources**: `SourceCard`

## 3. Session Flow
On new conversation, no session ID is initially provided. On the first `sendChatMessage` request, the backend creates a session in PostgreSQL and returns `session_id`. The frontend stores this in `activeSessionId` and passes it sequentially to maintain context.

## 4. Security Considerations
- Backend HTML is NEVER dangerously set. We use `react-markdown`.
- Source URLs are rendered from the backend payload.
- No API keys (Anthropic/OpenAI) are exposed in the frontend. All generation is securely proxied through the backend `/api/chat` route.

## 5. Artifact Security Model
Artifacts generated via the `generate_ship30` tool represent untrusted, dynamic output from LLMs. 
- **Persistence**: They are securely persisted using PostgreSQL via `ArtifactManager`.
- **Isolation**: On the frontend, the `ArtifactViewer` component uses `react-markdown` with `remarkGfm` to parse Ship 30 essays into a safe React AST.
- **Sanitization**: Raw HTML (`dangerouslySetInnerHTML`) is entirely prohibited. Any arbitrary `<script>` tags, event handlers (`onclick`), or `javascript:` URLs are naturally discarded during parsing.
- **Traceability**: All artifacts are fundamentally grounded to `SourceCitation` objects mapped in JSONB, completely blocking hallucinations from entering the artifact without a recorded trace.

## 6. Security & Resilience
- **Input Validation**: Pydantic strictly enforces string lengths (e.g., max 4000 chars for query) and UUID boundaries, protecting against payload flooding.
- **Prompt Injection Defense**: All untrusted LLM input (e.g., transcripts) is strictly encapsulated within `<transcript_context>` XML tags. The system prompt explicitly commands the model to treat the content as reference data and not executable instructions.
- **Database & Provider Resilience**: A global `SQLAlchemyError` exception handler ensures that DB connection losses result in a graceful HTTP 503 instead of crashing the server or leaking stack traces. The LLM provider layer implements a similar fallback and graceful failure response.
- **Observability**: A `RequestIDMiddleware` injects an `X-Request-ID` into every HTTP lifecycle, which is seamlessly attached to all structured backend logs using Python `logging.Filter` and `contextvars`.

## 7. Containerization & Networking
The application embraces a hybrid container architecture to maximize local performance:
- **Docker Compose**: Orchestrates the DB, Backend, and Frontend. Backend uses `depends_on` with `service_healthy` condition on the DB to prevent brittle race conditions.
- **Host Dependencies**: Ollama remains natively installed on the host machine to natively leverage hardware accelerators without complex GPU passthrough setups.
- **Communication Flow**: 
  - Browser (`localhost:3000`) -> Backend Container (`localhost:8000`)
  - Backend Container -> DB Container (`db:5432`)
  - Backend Container -> Host Ollama (`host.docker.internal:11434`)

## 8. Current Limitations
- No local storage caching for offline mode.
- Ollama local inference takes multiple minutes on CPU. The UI provides a "Thinking" state to prevent frozen experiences.

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

## 6. Current Limitations
- No local storage caching for offline mode.
- Ollama local inference takes multiple minutes on CPU. The UI provides a "Thinking" state to prevent frozen experiences.

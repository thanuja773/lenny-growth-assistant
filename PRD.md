# Product Requirements Document (PRD)

## Product Vision
An AI product intelligence workspace that answers product and growth questions based exclusively on Lenny's Podcast and Newsletter transcripts.

## Core Capabilities
1. **Grounded Conversational Q&A**: Retrieve relevant transcript content to answer user questions. Refuse to hallucinate if info is missing.
2. **Follow-up & Context**: Maintain session context for follow-up questions.
3. **Source Citations**: Clearly display sources used for generated answers.
4. **Content Generation**: "Convert to Ship 30 for 30" action to turn insights into short essays.
5. **In-app Artifact Viewer**: Safely view generated Markdown and HTML content without arbitrary script execution.
6. **LLM Flexibility**: Switch between local (Ollama) and cloud (OpenAI/Anthropic) models.
7. **History**: Access previous conversations and generated artifacts.

## Non-Functional Requirements
- **Performance**: Responsive UI, efficient vector search.
- **Security**: Secure rendering of AI-generated HTML (no XSS). No hardcoded secrets.
- **Reliability**: Graceful error handling, structured logging.
- **Deployability**: Docker-based reproducible startup.

## Out of Scope
- User authentication and billing.
- Mobile application.
- Kubernetes infrastructure.
- Complex multi-agent architectures.

import uuid
import logging
import json
from typing import List, Optional
from sqlalchemy.orm import Session
import anthropic

from app.core.config import settings
from app.services.llm.schemas import ChatRequest, ChatResponse, SourceCitation
from app.services.llm.service import SYSTEM_PROMPT
from app.services.llm.ollama import OllamaProvider
from app.services.llm.anthropic import AnthropicProvider

from .session_manager import SessionManager
from .artifact_manager import ArtifactManager
from .state import AgentState
from .tools.search_transcripts import SearchTranscriptsTool
from .tools.generate_ship30 import GenerateShip30Tool

logger = logging.getLogger("lenny_assistant.agent")

class GrowthAgent:
    def __init__(self, db: Session):
        self.db = db
        self.session_manager = SessionManager(db)
        self.artifact_manager = ArtifactManager(db)
        self.search_tool = SearchTranscriptsTool(db)
        
        # Tools definitions for Anthropic SDK
        self.tools_def = [
            {
                "name": "search_transcripts",
                "description": "Search the Lenny podcast transcripts for information to answer knowledge questions.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query."}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "generate_ship30",
                "description": "Generate a Ship 30 for 30 style essay on a given topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "The essay topic."},
                        "search_query": {"type": "string", "description": "The search query to gather evidence for the essay."}
                    },
                    "required": ["topic", "search_query"]
                }
            }
        ]

    def _format_history(self, messages) -> str:
        history = ""
        for msg in messages:
            history += f"{msg.role.capitalize()}: {msg.content}\n\n"
        return history

    def _execute_ollama_deterministic(self, state: AgentState) -> ChatResponse:
        logger.info("Executing Ollama deterministic agent routing.")
        provider = OllamaProvider()
        ship30_tool = GenerateShip30Tool(provider)
        
        # 1. Deterministic tool selection
        query_lower = state.query.lower()
        if "ship 30" in query_lower or "essay" in query_lower:
            state.selected_tool = "generate_ship30"
            topic = state.query
            search_query = topic
        else:
            state.selected_tool = "search_transcripts"
            search_query = state.query

        # 2. Retrieve Context (both tools need retrieval)
        history_text = "\n".join([f"{m['role']}: {m['content']}" for m in state.recent_history[-4:]])
        enhanced_query = f"{history_text}\nUser: {search_query}" if history_text else search_query
        
        search_result = self.search_tool.execute(enhanced_query, top_k=5)
        chunks = search_result["chunks"]
        sources = search_result["sources"]
        
        if not chunks:
            answer = "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently."
            return ChatResponse(
                session_id=str(state.session_id),
                answer=answer,
                sources=[],
                provider="ollama",
                model="llama3",
                retrieval_count=0,
                tool_used=state.selected_tool
            )

        # 3. Execute Selected Tool
        artifact_id = None
        if state.selected_tool == "generate_ship30":
            result = ship30_tool.execute(topic, chunks, sources)
            answer = result["content"]
            word_count = result["word_count"]
            model = "llama3"
            
            if word_count > 0:
                artifact = self.artifact_manager.create_artifact(
                    session_id=state.session_id,
                    artifact_type="ship30",
                    title=result["title"],
                    content=result["content"],
                    word_count=result["word_count"],
                    sources=sources
                )
                artifact_id = str(artifact.id)
        else:
            # Normal Chat via search_transcripts
            context_text = ""
            for i, chunk in enumerate(chunks, 1):
                context_text += f"\n[Source {i}]\nTranscript: {chunk['title']}\nText: {chunk['text']}\n"
            
            user_prompt = f"History:\n{history_text}\n\nContext:\n{context_text}\n\nUser Question: {state.query}"
            try:
                answer, model = provider.generate(SYSTEM_PROMPT, user_prompt, chunks)
                word_count = None
            except Exception as e:
                logger.error(f"Ollama generation failed: {e}")
                raise RuntimeError("LLM provider error") from e

        return ChatResponse(
            session_id=str(state.session_id),
            answer=answer,
            sources=sources,
            provider="ollama",
            model=model,
            retrieval_count=len(chunks),
            tool_used=state.selected_tool,
            word_count=word_count,
            artifact_id=artifact_id
        )

    def _execute_anthropic_sdk(self, state: AgentState) -> ChatResponse:
        logger.info("Executing Anthropic Claude Agent SDK routing.")
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key or api_key == "dummy_anthropic_key_for_testing":
            logger.warning("No valid Anthropic API key. Falling back to Ollama deterministic routing.")
            return self._execute_ollama_deterministic(state)
            
        client = anthropic.Anthropic(api_key=api_key)
        model = settings.ANTHROPIC_MODEL
        
        # Format history for Anthropic
        messages = [{"role": m["role"], "content": m["content"]} for m in state.recent_history]
        messages.append({"role": "user", "content": state.query})
        
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=self.tools_def
        )
        
        if response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_inputs = tool_use.input
            state.selected_tool = tool_name
            
            # Execute the tool
            if tool_name == "search_transcripts":
                search_result = self.search_tool.execute(tool_inputs["query"])
                chunks = search_result["chunks"]
                sources = search_result["sources"]
                
                # Second turn
                context_text = ""
                for i, chunk in enumerate(chunks, 1):
                    context_text += f"\n[Source {i}]\nTranscript: {chunk['title']}\nText: {chunk['text']}\n"
                
                if not chunks:
                    context_text = "No evidence found."
                    
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user", 
                    "content": [{"type": "tool_result", "tool_use_id": tool_use.id, "content": context_text}]
                })
                
                final_response = client.messages.create(
                    model=model,
                    max_tokens=2048,
                    system=SYSTEM_PROMPT,
                    messages=messages
                )
                answer = final_response.content[0].text
                
                if not chunks:
                    answer = "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently."
                
                return ChatResponse(
                    session_id=str(state.session_id),
                    answer=answer,
                    sources=sources,
                    provider="anthropic",
                    model=model,
                    retrieval_count=len(chunks),
                    tool_used=tool_name
                )
                
            elif tool_name == "generate_ship30":
                search_result = self.search_tool.execute(tool_inputs["search_query"])
                chunks = search_result["chunks"]
                sources = search_result["sources"]
                
                ship30_tool = GenerateShip30Tool(AnthropicProvider())
                result = ship30_tool.execute(tool_inputs["topic"], chunks, sources)
                
                artifact_id = None
                if result["word_count"] > 0:
                    artifact = self.artifact_manager.create_artifact(
                        session_id=state.session_id,
                        artifact_type="ship30",
                        title=result["title"],
                        content=result["content"],
                        word_count=result["word_count"],
                        sources=sources
                    )
                    artifact_id = str(artifact.id)
                
                return ChatResponse(
                    session_id=str(state.session_id),
                    answer=result["content"],
                    sources=sources,
                    provider="anthropic",
                    model=model,
                    retrieval_count=len(chunks),
                    tool_used=tool_name,
                    word_count=result["word_count"],
                    artifact_id=artifact_id
                )
        
        # No tool used
        state.selected_tool = "none"
        answer = response.content[0].text
        return ChatResponse(
            session_id=str(state.session_id),
            answer=answer,
            sources=[],
            provider="anthropic",
            model=model,
            retrieval_count=0,
            tool_used="none"
        )

    def process_request(self, request: ChatRequest) -> ChatResponse:
        # 1. Resolve Session
        if request.session_id:
            try:
                session_uuid = uuid.UUID(request.session_id)
                session = self.session_manager.get_session(session_uuid)
                if not session:
                    raise ValueError(f"Session {request.session_id} not found.")
            except ValueError as e:
                raise ValueError(f"Invalid session ID: {e}")
        else:
            session = self.session_manager.create_session()
            
        # 2. Build State
        history = self.session_manager.get_session_messages(session.id, limit=12)
        history_dicts = [{"role": m.role, "content": m.content} for m in history]
        
        primary_provider = request.provider or settings.LLM_PROVIDER or "ollama"
        if primary_provider not in ["ollama", "anthropic"]:
            raise ValueError(f"Unsupported LLM provider: {primary_provider}")
        
        state = AgentState(
            session_id=session.id,
            query=request.query,
            provider=primary_provider,
            recent_history=history_dicts
        )
        
        # 3. Route to specific provider agent
        try:
            if primary_provider == "anthropic":
                response = self._execute_anthropic_sdk(state)
            else:
                # Default to deterministic Ollama routing
                response = self._execute_ollama_deterministic(state)
                
            # 4. Persist interaction
            self.session_manager.add_message(session.id, "user", request.query)
            self.session_manager.add_message(session.id, "assistant", response.answer)
            
            logger.info(f"Agent processed request successfully. Session: {session.id}, Tool: {response.tool_used}, Sources: {response.retrieval_count}")
            return response
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise RuntimeError(f"Agent execution failed: {str(e)}")

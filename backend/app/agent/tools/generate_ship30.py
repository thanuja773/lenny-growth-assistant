from typing import List, Dict, Any, Tuple
import logging
from app.services.llm.base import LLMProvider
from app.services.llm.schemas import SourceCitation

logger = logging.getLogger("lenny_assistant.agent.tools.ship30")

SHIP30_SYSTEM_PROMPT = """You are Lenny Growth Assistant, a highly skilled writer specializing in Ship 30 for 30 style essays.
Your task is to write a compelling, 1,250-word essay about the provided topic using ONLY the provided Lenny transcript context as evidence.

Rules:
1. Target length: ~1,250 words.
2. Structure: Strong hook, narrative arc, skimmable headings, bullets, and bold key takeaways.
3. Content: Must be grounded entirely in the provided transcript context.
4. DO NOT fabricate facts, quotes, names, or recommendations.
5. If the context does not contain enough evidence to write a comprehensive essay, DO NOT invent claims. Instead, reply EXACTLY with:
"I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently."
6. Provide practical, actionable takeaways derived from the transcripts.
7. Maintain a professional, insightful, and engaging tone.
"""

class GenerateShip30Tool:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def execute(self, topic: str, source_context: List[Dict[str, Any]], sources: List[SourceCitation]) -> Dict[str, Any]:
        if not source_context:
            return {
                "title": topic,
                "content": "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently.",
                "word_count": 0,
                "sources": []
            }
            
        context_text = ""
        for i, chunk in enumerate(source_context, 1):
            context_text += f"\n[Source {i}]\nTranscript: {chunk['title']}\nText: {chunk['text']}\n"

        user_prompt = f"Topic: {topic}\n\nContext:\n{context_text}\n\nPlease generate the Ship 30 for 30 essay now."
        
        try:
            answer, model = self.provider.generate(SHIP30_SYSTEM_PROMPT, user_prompt, source_context)
            word_count = len(answer.split())
            
            # Check if LLM gracefully aborted
            if "couldn't find enough evidence" in answer or word_count < 50:
                return {
                    "title": topic,
                    "content": "I couldn't find enough evidence in the available Lenny transcript corpus to answer that confidently.",
                    "word_count": 0,
                    "sources": []
                }
            
            return {
                "title": f"Ship 30 for 30: {topic}",
                "content": answer,
                "word_count": word_count,
                "sources": sources
            }
        except Exception as e:
            logger.error(f"Ship30 generation failed: {e}")
            raise RuntimeError(f"Tool execution failed: {e}")

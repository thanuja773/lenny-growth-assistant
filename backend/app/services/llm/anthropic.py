import logging
from typing import Tuple

from app.core.config import settings
from .base import LLMProvider

try:
    from anthropic import Anthropic, APIError, APITimeoutError, APIConnectionError
except ImportError:
    Anthropic = None

logger = logging.getLogger("lenny_assistant.llm.anthropic")

class AnthropicProvider(LLMProvider):
    def __init__(self):
        if not Anthropic:
            raise RuntimeError("Anthropic SDK is not installed.")
        
        self.api_key = settings.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is missing or empty.")
            
        self.model = settings.ANTHROPIC_MODEL or "claude-3-haiku-20240307"
        self.timeout = settings.LLM_TIMEOUT_SECONDS
        
        self.client = Anthropic(api_key=self.api_key, timeout=self.timeout)

    def generate(self, system_prompt: str, user_prompt: str, context_chunks: list) -> Tuple[str, str]:
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            answer = response.content[0].text.strip()
            return answer, self.model
        except APITimeoutError:
            logger.error("Anthropic request timed out.")
            raise RuntimeError("LLM request timed out")
        except APIConnectionError:
            logger.error("Anthropic connection error.")
            raise RuntimeError("LLM provider unavailable")
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            raise RuntimeError("LLM provider error")
        except Exception as e:
            logger.error(f"Anthropic unknown error: {e}")
            raise RuntimeError("LLM provider error")

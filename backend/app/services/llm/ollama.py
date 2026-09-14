import logging
import requests
from typing import Tuple

from app.core.config import settings
from .base import LLMProvider

logger = logging.getLogger("lenny_assistant.llm.ollama")

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = (settings.OLLAMA_BASE_URL or "http://localhost:11434").rstrip("/")
        self.model = settings.OLLAMA_MODEL or "llama3"
        self.timeout = settings.LLM_TIMEOUT_SECONDS

    def generate(self, system_prompt: str, user_prompt: str, context_chunks: list) -> Tuple[str, str]:
        # Format the messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            answer = data.get("message", {}).get("content", "").strip()
            return answer, self.model
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out.")
            raise RuntimeError("LLM request timed out")
        except requests.exceptions.ConnectionError:
            logger.error("Ollama connection refused.")
            raise RuntimeError("LLM provider unavailable")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e.response.text}")
            if e.response.status_code == 404:
                raise RuntimeError(f"Ollama model '{self.model}' not found.")
            raise RuntimeError("LLM provider error")
        except Exception as e:
            logger.error(f"Ollama unknown error: {e}")
            raise RuntimeError("LLM provider error")

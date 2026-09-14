from abc import ABC, abstractmethod
from typing import Tuple

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, context_chunks: list) -> Tuple[str, str]:
        """
        Generate a response using the given prompts and context.
        Returns a tuple of (generated_answer, model_name).
        """
        pass

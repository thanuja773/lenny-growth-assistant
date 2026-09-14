import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.services.llm.ollama import OllamaProvider

provider = OllamaProvider()
try:
    answer, model = provider.generate("You are a helpful assistant.", "What makes a good product manager?", [])
    print("SUCCESS")
    print(answer)
except Exception as e:
    print("FAILED")
    import traceback
    traceback.print_exc()

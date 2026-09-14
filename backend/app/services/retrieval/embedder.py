import logging
from typing import List, Optional
from app.core.config import settings

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

logger = logging.getLogger("lenny_assistant.retrieval.embedder")


class QueryEmbedder:
    _instance: Optional["QueryEmbedder"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls) -> "QueryEmbedder":
        if cls._instance is None:
            cls._instance = super(QueryEmbedder, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self) -> None:
        if SentenceTransformer is None:
            logger.error("sentence-transformers package is not installed.")
            raise ImportError("sentence-transformers is not installed.")
        logger.info(f"Loading retrieval query embedding model: {settings.EMBEDDING_MODEL}")
        try:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Query embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{settings.EMBEDDING_MODEL}': {e}")
            self._model = None
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single search query into a 384-dimensional vector.
        Raises ValueError on empty/whitespace query.
        Raises RuntimeError if model is unavailable or embedding fails.
        """
        if not query or not query.strip():
            raise ValueError("Query string must not be empty or whitespace-only.")

        if self._model is None:
            self._init_model()

        try:
            cleaned_query = query.strip()
            embedding = self._model.encode(cleaned_query, convert_to_numpy=True)
            emb_list = embedding.tolist()

            if len(emb_list) != settings.EMBEDDING_DIMENSION:
                raise ValueError(
                    f"Expected embedding dimension {settings.EMBEDDING_DIMENSION}, got {len(emb_list)}"
                )

            return emb_list
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error generating embedding for query: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}") from e

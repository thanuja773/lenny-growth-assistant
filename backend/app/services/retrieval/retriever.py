import logging
import time
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.transcript import Transcript
from app.db.models.transcript_chunk import TranscriptChunk
from app.services.retrieval.embedder import QueryEmbedder
from app.services.retrieval.schemas import RetrievalResponse, SearchResultItem

logger = logging.getLogger("lenny_assistant.retrieval.service")


class RetrievalService:
    def __init__(self, db: Session, embedder: Optional[QueryEmbedder] = None) -> None:
        self.db = db
        self.embedder = embedder or QueryEmbedder()

    def search(self, query: str, top_k: Optional[int] = None) -> RetrievalResponse:
        """
        Perform semantic retrieval against transcript chunks using pgvector cosine distance.
        """
        start_time = time.perf_counter()

        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        cleaned_query = query.strip()
        k = top_k if top_k is not None else settings.RETRIEVAL_TOP_K
        if k < 1:
            raise ValueError("top_k must be at least 1.")
        if k > settings.RETRIEVAL_MAX_TOP_K:
            raise ValueError(f"top_k exceeds maximum allowed limit of {settings.RETRIEVAL_MAX_TOP_K}.")

        logger.info(f"Retrieval query: '{cleaned_query[:80]}' (top_k={k})")

        # 1. Embed query
        try:
            query_vector = self.embedder.embed_query(cleaned_query)
        except Exception as e:
            logger.error(f"Embedding failure during retrieval: {e}")
            raise

        # 2. Vector search in PostgreSQL using pgvector cosine distance
        candidate_pool_size = min(
            settings.RETRIEVAL_MAX_TOP_K * 2,
            max(settings.RETRIEVAL_CANDIDATE_POOL_SIZE, k * 3),
        )

        try:
            distance_expr = TranscriptChunk.embedding.cosine_distance(query_vector).label("distance")

            query_stmt = (
                self.db.query(
                    TranscriptChunk,
                    Transcript.title.label("transcript_title"),
                    Transcript.source_url.label("source_url"),
                    Transcript.source_type.label("source_type"),
                    Transcript.published_at.label("published_at"),
                    distance_expr,
                )
                .join(Transcript, TranscriptChunk.transcript_id == Transcript.id)
                .order_by(distance_expr.asc())
                .limit(candidate_pool_size)
            )

            raw_results = query_stmt.all()
        except Exception as e:
            logger.error(f"Database error during vector search: {e}")
            raise

        # 3. Filter candidates by similarity threshold
        # In pgvector: cosine distance d in [0, 2]. Cosine similarity s = 1 - d.
        candidates = []
        for chunk, title, url, stype, published, dist in raw_results:
            distance = float(dist) if dist is not None else 1.0
            similarity = round(max(0.0, min(1.0, 1.0 - distance)), 4)

            if similarity >= settings.RETRIEVAL_MIN_SIMILARITY:
                candidates.append(
                    SearchResultItem(
                        chunk_id=chunk.id,
                        transcript_id=chunk.transcript_id,
                        transcript_title=title,
                        source_url=url,
                        source_type=stype,
                        published_at=published,
                        chunk_index=chunk.chunk_index,
                        text=chunk.content,
                        similarity_score=similarity,
                    )
                )

        candidate_count = len(candidates)

        # 4. Lightweight diversity filtering
        final_results = self._apply_diversity(candidates, k)

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(
            f"Retrieval complete in {latency_ms}ms: {candidate_count} candidates above threshold "
            f"({settings.RETRIEVAL_MIN_SIMILARITY}), returning {len(final_results)} items."
        )

        return RetrievalResponse(
            query=cleaned_query,
            results=final_results,
            count=len(final_results),
        )

    def _apply_diversity(self, candidates: List[SearchResultItem], top_k: int) -> List[SearchResultItem]:
        """
        Deterministic lightweight diversity rule:
        Avoid picking immediately adjacent chunks (chunk_index diff <= 1) from the same transcript
        when alternative diverse candidates meeting the similarity threshold exist.
        If not enough diverse candidates exist, fallback gracefully to fill up to top_k.
        """
        if len(candidates) <= top_k:
            return candidates

        selected: List[SearchResultItem] = []
        deferred: List[SearchResultItem] = []

        for candidate in candidates:
            # Check if this candidate is an immediate neighbor of an already selected chunk from the same transcript
            is_neighbor = any(
                s.transcript_id == candidate.transcript_id and abs(s.chunk_index - candidate.chunk_index) <= 1
                for s in selected
            )

            if not is_neighbor and len(selected) < top_k:
                selected.append(candidate)
            else:
                deferred.append(candidate)

        # Fallback to deferred candidates if diversity filtering left open slots
        while len(selected) < top_k and deferred:
            selected.append(deferred.pop(0))

        return selected

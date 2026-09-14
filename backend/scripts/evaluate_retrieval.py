import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.services.retrieval.retriever import RetrievalService

EVALUATION_QUERIES = [
    "How do startups find product-market fit?",
    "How should founders prioritize product ideas?",
    "What makes a good product manager?",
    "How can teams conduct better user interviews?",
    "What advice is given about growth?",
]


def run_evaluation():
    db = SessionLocal()
    service = RetrievalService(db=db)

    print("=" * 70)
    print("STEP 3: RAG RETRIEVAL EVALUATION (Live PostgreSQL + pgvector)")
    print("=" * 70)

    try:
        for idx, query in enumerate(EVALUATION_QUERIES, 1):
            print(f"\nQUERY {idx}:")
            print(f"{query}\n")

            response = service.search(query=query, top_k=5)

            if not response.results:
                print("  No results found matching similarity threshold.")
                continue

            for rank, item in enumerate(response.results, 1):
                print(f"RESULT {rank}:")
                print(f"Transcript : {item.transcript_title}")
                print(f"Similarity : {item.similarity_score:.4f}")
                print(f"Source URL : {item.source_url}")
                print(f"Chunk Idx  : {item.chunk_index}")
                # Print clean snippet of text (first 300 characters)
                preview = item.text.replace("\n", " ").strip()
                if len(preview) > 300:
                    preview = preview[:297] + "..."
                print(f"Text       : {preview}\n")

            print("-" * 50)
    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation()

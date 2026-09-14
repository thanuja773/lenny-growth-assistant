# RAG Retrieval Service

## Overview
The retrieval service provides semantic search capabilities across ingested podcast and newsletter transcripts. It converts user queries into dense vector embeddings and performs cosine similarity search using PostgreSQL with the `pgvector` extension.

The retrieval layer is completely decoupled from generation, LLMs, and agentic layers. It outputs retrieved text chunks along with metadata and similarity scores.

## Architecture

```
User Query / API Client
         ↓
POST /api/retrieval/search
         ↓
RetrievalService
         ↓
QueryEmbedder (sentence-transformers/all-MiniLM-L6-v2)
         ↓ (384-dimensional dense vector)
PostgreSQL + pgvector (transcript_chunks <=> query_vector)
         ↓ (Candidate pool of up to max(15, top_k * 3))
Threshold Filter (similarity >= RETRIEVAL_MIN_SIMILARITY)
         ↓
Lightweight Diversity Filter (suppresses immediate consecutive chunks from same transcript)
         ↓
Top-K SearchResultItems (text + metadata + scores)
```

## Key Components

### 1. Local Query Embedding
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Execution**: Runs locally via PyTorch/Hugging Face transformers. No cloud API keys or external services required.
- **Caching**: The `QueryEmbedder` is a singleton ensuring the embedding weights are loaded once in memory and reused across queries.
- **Validation**: Empty and whitespace-only queries are rejected with an explicit validation error.

### 2. pgvector Cosine Search
- **SQL Operator**: Cosine distance operator (`<=>`).
- **Score Calculation**: 
  $$\text{Cosine Similarity} = 1.0 - \text{Cosine Distance}$$
  Scores are bounded within $[0.0, 1.0]$ and formatted to 4 decimal places.
- **Ordering**: Results are strictly ordered by similarity in descending order (distance ascending).

### 3. Top-K & Pool Oversampling
- **Default Top-K**: 5 (`RETRIEVAL_TOP_K`)
- **Maximum Top-K**: 20 (`RETRIEVAL_MAX_TOP_K`)
- **Candidate Pool**: When retrieving $K$ items, the query oversamples up to $\min(40, \max(15, 3K))$ chunks before thresholding and diversity filtering.

### 4. Similarity Threshold
- **Threshold**: Configured via `RETRIEVAL_MIN_SIMILARITY` (default `0.30`).
- **Empty Retrieval Behavior**: If no candidate chunk achieves a similarity score $\ge 0.30$, the service returns an empty list (`results: []`, `count: 0`) with HTTP 200. This deliberate design enables downstream components to acknowledge a lack of relevant evidence instead of hallucinating on low-relevance content.

### 5. Lightweight Diversity Strategy
- In transcripts, consecutive chunks frequently share substantial context due to rolling chunk overlap and ongoing conversational topics.
- To prevent top results from being dominated by repetitive neighboring turns (e.g., chunk 14, 15, and 16 of the same episode), the diversity filter suppresses immediately adjacent chunks (`|chunk_index_a - chunk_index_b| <= 1`) from the same transcript when diverse candidates from other parts or episodes meeting the threshold are available.
- If insufficient non-neighboring candidates exist, the filter gracefully backfills open slots to honor the requested `top_k`.

### 6. Source Traceability
Each retrieved item includes full provenance:
- `chunk_id`: Unique UUID of the chunk
- `transcript_id`: UUID of the parent transcript
- `transcript_title`: Title of the episode
- `source_url`: Public GitHub repository link to original markdown transcript
- `source_type`: Category (`podcast`)
- `chunk_index`: Sequence position within the transcript
- `text`: Chunk text excerpt
- `similarity_score`: Computed cosine similarity score

### 7. Security & Untrusted Content
- Retrieved text originates from external transcripts and is treated strictly as untrusted data.
- The retrieval service only performs text extraction and similarity scoring; it never executes code or evaluates prompt instructions embedded in chunk text.

## API Specification

### Endpoint: `POST /api/retrieval/search`

#### Request Body
```json
{
  "query": "How do startups find product-market fit?",
  "top_k": 5
}
```

#### Successful Response (`200 OK`)
```json
{
  "query": "How do startups find product-market fit?",
  "results": [
    {
      "chunk_id": "8f87a8ad-fbf4-4f24-912a-6a56c4d44aa5",
      "transcript_id": "0d5d0a0a-cb4f-4207-b303-6f344a6a0589",
      "transcript_title": "Ada Chen Rekhi",
      "source_url": "https://github.com/ChatPRD/lennys-podcast-transcripts/tree/main/episodes/ada-chen-rekhi/transcript.md",
      "source_type": "podcast",
      "published_at": null,
      "chunk_index": 4,
      "text": "Lenny (05:20): ...",
      "similarity_score": 0.5842
    }
  ],
  "count": 1
}
```

#### Error Responses
- **`400 Bad Request`**: Empty query string, `top_k < 1`, or `top_k > 20`.
- **`503 Service Unavailable`**: Database or embedding model runtime failure.

## Known Limitations
1. **Dense-Only Retrieval**: Current implementation relies exclusively on dense embeddings. Keyword-specific queries (exact acronyms, specialized jargon) can benefit from hybrid search combining BM25/sparse lexical search with dense vectors.
2. **Chunking Boundary Sensitivity**: Chunks are split around ~700 tokens with 100 token overlap. Relevant context spanning across chunk boundaries can suffer slightly degraded similarity if key phrases are split.
3. **Similarity Threshold Tuning**: The default threshold of `0.30` is an empirical baseline for MiniLM cosine similarity. Specific domains or question types may require fine-tuning or dynamic calibration.

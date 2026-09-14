# Ingestion Pipeline

## 1. Data source
- **Source**: Lenny's Podcast / Newsletter transcript repository
- **URL**: `https://github.com/ChatPRD/lennys-podcast-transcripts`

## 2. Why this source was selected
The repository was discovered by parsing the assignment's explicit requirements to use the "EXACT Lenny Podcast / Newsletter transcript repository" linked in the brief. This is the official public archive of the transcripts.

## 3. Data format
- The data is organized in folders under `episodes/`. Each folder corresponds to an episode (e.g. `ada-chen-rekhi`).
- Each folder contains a `transcript.md` file in plain Markdown text.
- Metadata is implicitly inferred from the folder path. Text is labeled with speakers and timestamps (e.g. `Lenny (01:11:40):`).

## 4. Raw data location
Downloaded raw `.md` files are stored in `data/raw/` at the project root.

## 5. Cleaning process
- Removed excessive blank lines (more than 2 consecutive newlines are normalized to double newlines).
- Stripped leading/trailing whitespace per line.
- Intentionally preserved speaker names and timestamps to retain conversational context for LLM grounding.

## 6. Chunking strategy
- Chunks are roughly 700 tokens in size with an overlap of 100 tokens. 
- We respect paragraph/speaker boundaries by splitting on double newlines (`\n\n`) and grouping them rather than blindly slicing at random character boundaries. 
- Using standard token-to-word estimations (`token_count ≈ word_count * 1.3`).

## 7. Embedding model
- Local HuggingFace sentence-transformer: `sentence-transformers/all-MiniLM-L6-v2`
- This ensures high quality standard embeddings without relying on a paid API (like OpenAI) for ingestion.

## 8. Embedding dimension
- **384** (Matches the `all-MiniLM-L6-v2` model output).
- The vector column in PostgreSQL pgvector is correctly typed to 384 dimensions.

## 9. Database storage
- Stored in PostgreSQL with `pgvector` enabled.
- Tables: `transcripts` (stores metadata) and `transcript_chunks` (stores text and embeddings).

## 10. Idempotency strategy
- The script uses `source_url` as a deterministic identifier.
- If a transcript is re-ingested, the pipeline detects the existing record, deletes the old chunks associated with its ID, updates its metadata, and writes the new chunks.
- This allows safe repeated executions without duplicating records.

## 11. CLI usage
Run the pipeline using the command line:
```bash
python -m ingestion.__main__ --limit 3
```
Options:
- `--limit N`: Restrict ingestion to the first N episodes.
- `--dry-run`: Parse and chunk files without persisting to the database.

## 12. Testing
- Run tests with: `pytest ingestion/tests/`
- Validates metadata parsing, text cleaning, chunking boundaries, and embedder dimensions.

## 13. Troubleshooting
- **GitHub Rate Limit**: If `requests` fails with a 403, GitHub API rate limits have been hit. Consider using a `GITHUB_TOKEN` environment variable if needed.
- **Model Download Error**: The first run downloads `all-MiniLM-L6-v2`. If it fails, ensure you have an active internet connection.
- **Database Error**: Ensure `docker-compose up -d` is running and `alembic upgrade head` was executed to create the tables.

# Mutual Fund FAQ Assistant

A lightweight Retrieval-Augmented Generation (RAG) assistant for factual mutual fund queries about HDFC schemes.

## Overview
This project uses a curated corpus of official HDFC, AMFI, SEBI, and Groww sources to answer factual questions with source-backed responses.

## Phase 0 - Project Setup
- Project structure created
- Python dependencies documented
- Git ignore configured
- README skeleton initialized

## Project Structure
- `src/` - source code
- `tests/` - unit and integration tests
- `data/` - parsed corpus and embeddings
- `implementation-plan-v2.md` - practical development plan
- `architecture.md` - system architecture overview
- `context.md` - project context and corpus definitions

## Getting Started
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the environment:
   - Windows: `.
venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the ingestion pipeline:
   ```bash
   python -m src.ingest
   ```
   This populates `data/corpus.json` and `data/corpus.db`.

## Next Steps
- Implement corpus ingestion and structured parsing
- Add chunking and embedding generation (Embedding model: BAAI/bge-small-en-v1.5; Vector store: ChromaDB)
- Build retrieval, RAG orchestration, and the query API
- Create a lightweight frontend interface

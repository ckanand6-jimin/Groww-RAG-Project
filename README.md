# Groww RAG-Based Mutual Fund FAQ Chatbot

A facts-only Retrieval-Augmented Generation (RAG) chatbot built for HDFC Mutual Fund schemes using ChromaDB, Groq LLM, and official mutual fund source documents.

## Project Overview

This project answers factual mutual fund questions using a curated corpus sourced from:

* HDFC Mutual Fund
* AMFI
* SEBI
* Groww

The system supports retrieval-based question answering and refuses investment advice queries.

## Features

* Facts-only mutual fund assistant
* Query classification
* Refusal handling for advisory queries
* ChromaDB vector search
* Groq-powered answer generation
* Source-backed responses
* Scheduled corpus refresh
* Automated testing suite

## Supported Queries

Examples:

* What is the expense ratio of HDFC Mid Cap Fund?
* What is the benchmark of HDFC Mid Cap Fund?
* What is the AUM of HDFC Defence Fund?
* What is the riskometer classification of HDFC Defence Fund?
* Who is the fund manager of HDFC Large Cap Fund?
* What is the exit load of HDFC Small Cap Fund?

## Unsupported Queries

Examples:

* Should I invest in HDFC Mid Cap Fund?
* Which HDFC fund is best?
* Can you recommend a mutual fund?

These queries return an educational refusal response because the system does not provide investment advice.

---

# Architecture

User Query

↓

Query Classifier

↓

Retriever (ChromaDB)

↓

RAG Layer

↓

Groq LLM

↓

Answer + Source Attribution

## Project Structure

```text
src/
├── app.py
├── rag.py
├── retrieve.py
├── query_classifier.py
├── ingest.py
├── chunk.py
├── embed.py
├── vector_db.py
├── scheduler.py

tests/
├── test_query_classifier.py
├── test_retrieval.py
├── test_rag.py
├── test_smoke.py

data/
├── corpus.json
├── chunks.json
├── chroma/

Docs/
├── architecture.md
├── context.md
├── implementation-plan-v2.md
├── edge-case.md

```

## Setup

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

Windows:

```powershell
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key
ENABLE_SCHEDULER=1
```

## Build Corpus

```bash
python -m src.ingest
python -m src.chunk
```

## Create Vector Database

```bash
python -c "from src.vector_db import upsert_chunks_into_chroma; upsert_chunks_into_chroma(force_refresh=True)"
```

## Run Application

```bash
uvicorn src.app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Scheduler

The scheduler refreshes the corpus daily at:

```text
10:00 AM
```

Enable scheduler:

```env
ENABLE_SCHEDULER=1
```

## Testing

Run all tests:

```bash
python -m pytest -v
```

Current Status:

```text
8 tests passed
```

## Evaluation Summary

Validated modules:

* Query Classification
* Retrieval
* Response Generation
* Refusal Handling
* Scheduler Integration

## Disclaimer

This project provides factual mutual fund information only.

It does not provide:

* Investment advice
* Portfolio recommendations
* Buy/Sell suggestions
* Financial planning guidance

Users should consult a qualified financial advisor before making investment decisions.

# Groww RAG-Based Mutual Fund FAQ Chatbot

A facts-only Retrieval-Augmented Generation (RAG) chatbot built for HDFC Mutual Fund schemes using ChromaDB, Groq LLM, and official mutual fund source documents.

---

# Project Overview

This project provides facts-only answers about selected HDFC Mutual Fund schemes using information retrieved from official public sources.

The chatbot uses Retrieval-Augmented Generation (RAG) and refuses investment advice or recommendation-based questions.

## Covered Schemes

1. HDFC Large Cap Fund
2. HDFC Mid Cap Fund
3. HDFC Small Cap Fund
4. HDFC Equity Fund
5. HDFC ELSS Tax Saver Fund
6. HDFC Balanced Advantage Fund
7. HDFC Nifty 50 Index Fund
8. HDFC Defence Fund
9. HDFC Gold ETF Fund of Fund
10. HDFC Liquid Fund

## Source Corpus

The corpus contains information collected from:

* HDFC Mutual Fund official documents
* HDFC KIM documents
* HDFC SID documents
* AMFI investor education resources
* SEBI investor education resources
* Groww mutual fund scheme pages

---

# Features

* Facts-only mutual fund assistant
* Query classification
* Refusal handling for advisory queries
* ChromaDB vector search
* Groq-powered answer generation
* Source-backed responses
* Scheduled corpus refresh
* Automated testing suite

---

# Supported Queries

Examples:

* What is the expense ratio of HDFC Mid Cap Fund?
* What is the benchmark of HDFC Mid Cap Fund?
* What is the AUM of HDFC Defence Fund?
* What is the riskometer classification of HDFC Defence Fund?
* Who is the fund manager of HDFC Large Cap Fund?
* What is the exit load of HDFC Small Cap Fund?

# Unsupported Queries

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

---

# Project Structure

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
├── sources.md
├── sample_qa.md
├── disclaimer.md
```

---

# Setup

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Environment

Windows:

```powershell
.venv\Scripts\activate
```

## Install Dependencies

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

---

# Deployment

## Railway Backend

Production URL:

https://groww-rag-project-production.up.railway.app

The application is deployed on Railway and serves the chatbot UI and FastAPI backend.

---

# Scheduler

The scheduler refreshes the corpus daily at:

```text
10:00 AM IST
```

Enable scheduler:

```env
ENABLE_SCHEDULER=1
```

---

# Testing

Run all tests:

```bash
python -m pytest -v
```

Current Status:

```text
8 tests passed
```

---

# Evaluation Summary

Validated modules:

* Query Classification
* Retrieval
* Response Generation
* Refusal Handling
* Scheduler Integration

---

# Known Limitations

* Supports only the selected HDFC Mutual Fund schemes included in the corpus.
* Answers depend on the information available in the indexed source documents.
* Some fields such as minimum SIP amount, capital gains certificate download process, or other operational details may not be available for all schemes.
* The chatbot does not calculate returns or compare scheme performance.
* The chatbot does not provide investment advice, recommendations, or portfolio suggestions.
* Responses are limited to retrieved source information and may refuse questions outside the corpus scope.

---

# Disclaimer

This project provides factual mutual fund information only.

It does not provide:

* Investment advice
* Portfolio recommendations
* Buy/Sell suggestions
* Financial planning guidance

Users should consult a qualified financial advisor before making investment decisions.

# Deployment Plan – Groww RAG Mutual Fund Assistant

## Architecture

Frontend:

* Static HTML/CSS/JS UI
* Hosted on Vercel

Backend:

* FastAPI
* Hosted on Railway

Vector Store:

* ChromaDB

Embeddings:

* BAAI/bge-small-en-v1.5

LLM:

* Groq API

Scheduler:

* GitHub Actions
* Daily refresh at 10:00 AM IST

---

## Environment Variables

Backend

GROQ_API_KEY=
GROQ_MODEL=
CHROMA_COLLECTION=mutual_fund_chunks
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
ENABLE_SCHEDULER=0

---

## GitHub Actions Scheduler

Workflow File

.github/workflows/refresh-corpus.yml

Schedule

10:00 AM IST
04:30 UTC

Responsibilities

* Run ingestion
* Run chunking
* Refresh embeddings
* Update Chroma collection

---

## Railway Deployment

Create Railway Project

Connect GitHub Repository

Repository

Groww-RAG-Project

Start Command

uvicorn src.app:app --host 0.0.0.0 --port $PORT

Add Environment Variables

Deploy

Verify

/health
/query
/refresh-status

---

## Vercel Deployment

Import GitHub Repository

Framework

Other

Frontend Directory

src/static

Environment Variable

BACKEND_URL=<railway-url>

Deploy

Verify

Chat UI loads
Queries reach backend
Source links work

---

## Local Testing Checklist

Backend starts successfully

uvicorn src.app:app --reload

Frontend loads

http://127.0.0.1:8000

Tests pass

python -m pytest -v

Scheduler logs generated

data/logs/refresh.log

---

## Production Verification

Factual query returns source-backed answer

Advisory query returns refusal response

Refresh status endpoint operational

Scheduler executes daily corpus refresh

Frontend communicates with backend successfully

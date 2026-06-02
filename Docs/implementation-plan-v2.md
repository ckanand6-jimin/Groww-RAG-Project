# Implementation Plan V2

This plan is a practical, phase-wise implementation guide for a single-developer build of the Mutual Fund FAQ Assistant. It follows the project corpus, architecture, and facts-only response requirements.

## Phase 0 – Project Setup

### Goal
Prepare a local development environment and project structure for building the RAG assistant.

### Tasks
- Create project folder structure with source, data, docs, and tests directories
- Initialize Git repository and `.gitignore`
- Set up Python virtual environment and install core libraries (FastAPI, requests, BeautifulSoup, transformers, torch, chromadb, SQLite/PostgreSQL client)
- Create basic README outline and architecture references

### Deliverables
- Local repository initialized
- Virtual environment with required packages installed
- Base project structure created
- README skeleton established

### Exit Criteria
- `git status` clean with initial files committed
- Python environment works and dependencies install successfully
- Basic project folders present

### Dependencies
- None beyond local machine and internet access for package installs

## Phase 1 – Corpus & Ingestion Pipeline

### Goal
Collect and parse the official source corpus to create structured scheme data.

### Tasks
- Define the 16 source URLs from `context.md`
- Build a small web scraper/parser for Groww HDFC scheme pages
- Build a parser for HDFC official KIM/SID/document guide pages
- Normalize extracted data into a consistent schema
- Save parsed data to JSON/SQLite for later use

### Deliverables
- Source URL list documented in code or config
- Scraper scripts for Groww and HDFC pages
- Structured dataset of HDFC scheme facts
- Basic ingestion script run successfully

### Exit Criteria
- Parsed data exists for all 10 HDFC fund pages and 4 HDFC official documents
- Structured data passes schema validation for required fields
- Data saved locally in a reusable format

### Dependencies
- Phase 0 completed

## Phase 2 – Chunking & Embeddings

### Goal
Convert the structured corpus into retrievable embeddings for semantic search.

### Tasks
- Define chunking rules for scheme facts and regulatory content using the cleaned NEXT_DATA output as primary source
- Chunk parsed content by semantic sections: overview, expense_ratio, exit_load, minimum_investment, benchmark, riskometer, fund_management, investment_objective, fund_house, plus raw document summaries
- Extract both human-readable text and structured values into chunk payloads
	- Fallback to cleaned HTML text only when structured NEXT_DATA fields are missing
	- Generate embeddings using a lightweight model (e.g. BAAI/bge-small-en-v1.5 for local development; upgrade path to BAAI/bge-large-en-v1.5 for higher quality)
	- Store chunk metadata with scheme ID, source URL, section name, and field-level provenance

### Deliverables
- Chunking script that uses section-based, structured chunk creation
- Embedding generation script
- Local store of embeddings and metadata with source and section tags

### Exit Criteria
- All corpus text is chunked and embedded
- Chunks include source URL, scheme ID, and content metadata
- Embeddings can be loaded successfully by the retrieval module

### Dependencies
- Phase 1 completed

## Phase 3 – Vector Database & Retrieval

### Goal
Implement a retrieval layer that can search the corpus using semantic similarity.

### Tasks
- Choose a vector store with metadata-filtering support (recommend ChromaDB for local development; production alternatives: Pinecone, Milvus, or Weaviate)
- Load embeddings and metadata into the store
- Implement query-side embedding generation with the same BGE model
- Build a retrieval function returning top-K relevant chunks from ChromaDB
- Support metadata-filtered search by scheme_id and section
- Add simple ranking by source authority and scheme relevance

### Deliverables
- Vector store initialized with corpus embeddings
- Retrieval module with search API
- Example queries returning relevant documents
- `src/retrieve.py` implemented for query embedding, metadata filtering, and reranking

### Exit Criteria
- Query results return relevant chunks for sample factual queries
- Retrieval module supports top-K results and metadata inspection
- Retrieval includes metadata-filtered scheme and section search
- Ranking prioritizes official source links where applicable

### Dependencies
- Phase 2 completed

## Phase 4 – RAG Orchestrator

### Goal
Combine retrieval output with a response composer to build citation-backed answers using Groq as the LLM.

### Tasks
- Create a RAG orchestrator module that accepts a user query
- Retrieve relevant chunks from the vector store
- Extract the most relevant fact and source link
- Format the answer into a 1-3 sentence response
- Use Groq to compose the final answer when available
- Attach exactly one citation and `Last updated from sources: <date>` footer

### Deliverables
- RAG orchestrator script/module
- Response composer that builds valid answer payloads
- Example outputs for factual queries
- `src/rag.py` implemented for Groq prompt composition and fallback handling
- `src/app.py` query endpoint for live question answering

### Exit Criteria
- RAG orchestrator returns a complete response payload for sample queries
- Each response includes one citation and required footer
- Responses are concise and fact-oriented
- Groq integration is supported via `GROQ_API_KEY` and `GROQ_MODEL`

### Dependencies
- Phase 3 completed

## Phase 5 – Query Classification & Refusal Handling

### Goal
Detect advisory queries and ensure the assistant refuses non-factual requests.

### Tasks
- Implement query preprocessing (lowercase, punctuation removal)
- Define advisory keyword patterns from `context.md`
- Build classification logic for factual vs advisory/ambiguous queries
- Create refusal response templates with a regulatory educational link
- Ensure factual-only queries proceed to retrieval

### Deliverables
- Query classifier module
- Refusal handling module with templates
- Test cases for advisory and factual queries
- `src/query_classifier.py` implemented for advisory/factual classification

### Exit Criteria
- Advisory questions return refusal responses consistently
- Factual queries continue through the RAG pipeline
- Refusal responses contain a polite, facts-only message and education link

### Dependencies
- Phase 4 completed

## Phase 6 – Scheduler & Corpus Refresh

### Goal
Automate daily corpus ingestion to keep data fresh.

### Tasks
- Add a scheduler using APScheduler or cron-like Python scheduling
- Schedule the ingestion pipeline to run daily at 10:00 AM IST
- Ensure refreshed data updates stored corpus and embeddings
- Implement a simple change detection report for ingestion runs

### Deliverables
- Scheduler configuration and startup script
- Daily ingestion workflow automated at 10:00 AM IST
- Refresh log file or report for each run

### Exit Criteria
- Scheduler triggers ingestion successfully at 10:00 AM IST daily
- Corpus data and embeddings are refreshed after each run
- Logs show ingestion status and any failures

### Dependencies
- Phase 1 completed
- Phase 2 completed

## Phase 7 – UI Integration

### Goal
Build a minimal interface that accepts questions and displays source-backed answers.

### Tasks
- Create a simple web UI using plain HTML/JS or minimal React
- Add a welcome message, disclaimer, and example questions
- Connect the UI to the backend query API
- Display response text, source link, and footer
- Handle advisory refusals gracefully in the UI

### Deliverables
- Lightweight frontend interface
- Backend API endpoint for `/query`
- UI showing answer text and citation link

### Exit Criteria
- User can submit a question from the UI and receive a response
- Advisory questions render refusal messages clearly
- Source citations and last-updated footer appear in UI answers

### Dependencies
- Phase 5 completed
- Phase 4 completed

## Phase 8 – Testing & Evaluation

### Goal
Validate the system with factual and refusal scenarios and ensure reliability.

### Tasks
- Write unit tests for ingestion, retrieval, classification, and response generation
- Create sample factual queries covering expense ratio, SIP, exit load, riskometer, benchmark, and statements
- Test refusal handling for advisory queries
- Evaluate response quality against source documents
- Fix bugs and refine response formatting

### Deliverables
- Test suite covering all core modules
- A documented set of sample query results
- Issue list and fixes applied

### Exit Criteria
- Core tests pass for ingestion, retrieval, and classification
- Sample queries return accurate, citations-backed answers
- Refusal handling works for advisory queries

### Dependencies
- Phase 7 completed

## Phase 9 – README & Deployment

### Goal
Document the project and prepare a simple local deployment path.

### Tasks
- Write a concise README with setup, run, and usage instructions
- Document the source corpus and architecture assumptions
- Add instructions for scheduling and refreshing the corpus
- Provide a minimal local deployment command or script

### Deliverables
- `README.md` with installation and usage steps
- `implementation-plan-v2.md` created as the practical plan
- Deployment notes for local execution

### Exit Criteria
- README clearly explains how to run the system locally
- Scheduler and query API startup steps are documented
- A developer can reproduce the system from the README

### Dependencies
- All previous phases completed

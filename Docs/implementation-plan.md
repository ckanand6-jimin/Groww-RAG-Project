# Phase-Wise Implementation Plan - Mutual Fund FAQ Assistant

## Overview
This document outlines the phased approach to building the Mutual Fund FAQ Assistant (Facts-Only Q&A). The plan is organized into 7 implementation phases spanning 24-28 weeks, with clear deliverables, milestones, and dependencies.

**Project Duration:** ~6-7 months
**Team Size:** 4-6 developers (Backend, Frontend, Data Engineer, QA)
**Start Date:** June 2026
**End Date:** December 2026

---

## Phase 1: Planning, Setup & Infrastructure (Weeks 1-2)

### Objectives
- Finalize project requirements and success criteria
- Set up development environment and tools
- Create data architecture blueprints
- Establish governance and compliance framework

### Key Activities

#### 1.1 Project Kickoff & Stakeholder Alignment
- Confirm project scope with stakeholders (Groww, HDFC, product team)
- Review regulatory requirements (SEBI, AMFI compliance guidelines)
- Define success metrics and KPIs
  - Response accuracy target: >95%
  - Advisory query refusal accuracy: >98%
  - Citation validity: 100%
  - Average response time: <2 seconds
  - System uptime: >99.5%

#### 1.2 Technology Stack Finalization
- Backend Framework: **Python FastAPI** (lightweight, async support)
- Vector Database: **ChromaDB** (local persistent store; production alternatives: Pinecone, Milvus, Weaviate)
- Structured Database: **PostgreSQL** (reliable, JSONB support)
- Embedding Model: **BAAI/bge-small-en-v1.5** (primary for local development)
- Frontend: **React + Tailwind CSS** (modern, responsive)
- Scheduler: **APScheduler** (Python task scheduling)
- Deployment: **Docker + AWS EC2**

#### 1.3 Development Environment Setup
- GitHub repository with branch protection rules
- CI/CD pipeline skeleton (GitHub Actions)
- Development, staging, and production environments
- Logging and monitoring infrastructure (ELK stack or CloudWatch)
- Documentation repository (Confluence/Notion)

#### 1.4 Data Governance Framework
- Data source documentation (16 URLs cataloged)
- Data freshness policy (daily refresh)
- Confidence scoring mechanism
- Source cross-verification process
- Audit trail for compliance

#### 1.5 Compliance & Security Setup
- Privacy impact assessment (PII handling)
- Regulatory compliance checklist (SEBI, AMFI)
- Security audit plan
- Data encryption strategy (TLS for APIs, encryption at rest)
- Rate limiting and DDoS protection

### Deliverables
- [ ] Project Charter & Stakeholder Alignment Document
- [ ] Technology Stack Decision Matrix
- [ ] Development Environment Setup Guide
- [ ] Data Governance & Compliance Checklist
- [ ] Risk Assessment & Mitigation Plan

### Timeline
- Week 1: Requirements & stakeholder alignment
- Week 2: Tech stack finalization & environment setup

### Success Criteria
- All stakeholders sign off on project scope
- Development environment functional for all team members
- Compliance framework documented and reviewed

---

## Phase 2: Data Ingestion Infrastructure (Weeks 3-6)

### Objectives
- Build web scraping and data extraction pipeline
- Implement daily scheduler for corpus refresh
- Create data validation and cross-verification layer
- Establish fact verification workflow

### Key Activities

#### 2.1 Web Scraping Module Development
- Create URL parser for Groww pages
  - Extract scheme metadata (name, expense ratio, AUM, fund manager)
  - Extract investment details (min SIP, lump sum, exit load)
  - Extract riskometer and benchmark data
- Create HDFC official parser
  - Parse KIM document links and summaries
  - Parse SID document links and summaries
  - Extract investor services information
  - Extract account statement download process
- Create regulatory body parser
  - AMFI investor education content
  - SEBI mutual fund guidance
- **Implementation Technology:** BeautifulSoup4, Selenium (for JavaScript-heavy pages)

#### 2.2 Data Extraction Pipeline
- HTML to structured JSON conversion
- Text normalization and tokenization
- Metadata extraction engine
- Link preservation and validation
- Error handling and retry mechanism
- **Output Format:** Standardized JSON schema per FUND_SCHEME definition

#### 2.3 Data Validation Layer
- Schema validation (ensure all required fields present)
- Data type checking (expense ratio is percentage, AUM is numeric)
- Consistency checks (compare data across multiple sources)
- Anomaly detection (flag if expense ratio changes > 0.1%)
- Cross-source verification (flag conflicts between Groww and HDFC)

#### 2.4 Scheduler Implementation
- **Tool:** APScheduler with persistent job store
- **Trigger:** Daily at 2 AM IST (off-peak hours)
- **Workflow:**
  1. Fetch all 16 URLs
  2. Extract and parse data
  3. Validate against schema
  4. Compare with previous day's data
  5. Generate anomaly report
  6. Update database with validated data
  7. Log ingestion results
- **Error Handling:** Retry failed URLs 3 times, notify admins on critical failures
- **Monitoring:** Track ingestion success rate, data freshness

#### 2.5 Database Schema Implementation
- PostgreSQL tables:
  ```sql
  CREATE TABLE schemes (
    scheme_id VARCHAR(100) PRIMARY KEY,
    scheme_name VARCHAR(255),
    scheme_type VARCHAR(50),
    expense_ratio DECIMAL(5,2),
    min_lump_sum BIGINT,
    min_sip BIGINT,
    current_aum BIGINT,
    exit_load DECIMAL(5,2),
    exit_load_period VARCHAR(100),
    lock_in_days INT,
    riskometer VARCHAR(50),
    benchmark_index VARCHAR(255),
    fund_manager_name VARCHAR(255),
    fund_manager_experience INT,
    inception_date DATE,
    last_updated TIMESTAMP,
    data_version INT,
    confidence_score DECIMAL(3,2)
  );
  
  CREATE TABLE scheme_sources (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(100) REFERENCES schemes(scheme_id),
    source_type VARCHAR(50), -- 'groww', 'hdfc_kim', 'hdfc_sid', etc.
    source_url VARCHAR(500),
    last_verified TIMESTAMP,
    verification_status VARCHAR(50) -- 'active', 'dead', 'changed'
  );
  
  CREATE TABLE fund_documents (
    id SERIAL PRIMARY KEY,
    scheme_id VARCHAR(100) REFERENCES schemes(scheme_id),
    document_type VARCHAR(50), -- 'kim', 'sid', 'factsheet', 'prospectus'
    document_url VARCHAR(500),
    last_updated TIMESTAMP
  );
  
  CREATE TABLE ingestion_logs (
    id SERIAL PRIMARY KEY,
    ingestion_date DATE,
    total_urls_processed INT,
    successful_extractions INT,
    failed_extractions INT,
    anomalies_detected INT,
    execution_time_seconds INT,
    status VARCHAR(50) -- 'success', 'partial', 'failed'
  );
  ```

#### 2.6 Fact Verification Workflow
- Primary source identification (Groww > HDFC > AMFI/SEBI)
- Cross-reference checking (verify key facts across 2+ sources)
- Confidence scoring:
  - 1.0: Exact match across 2+ official sources
  - 0.8: Match across Groww + HDFC
  - 0.6: Single source (most recent)
  - 0.4: Data >30 days old
  - <0.4: Flagged as low-confidence
- Anomaly alerts:
  - Expense ratio change > 0.1% → Notify admin
  - Fund manager change → Notify admin
  - URL returns 404 → Notify admin
  - Missing data fields → Flag in logs

### Deliverables
- [ ] Web Scraping Module (BeautifulSoup + Selenium)
- [ ] Data Extraction Pipeline with error handling
- [ ] Data Validation Engine
- [ ] Scheduler Implementation (APScheduler)
- [ ] PostgreSQL Database with schemas
- [ ] Ingestion Monitoring Dashboard
- [ ] Data Quality Report (daily automated)
- [ ] Ingestion Module Tests (80%+ coverage)

### Timeline
- Week 3: Web scraping module for Groww & HDFC
- Week 4: Data extraction pipeline & validation layer
- Week 5: Scheduler implementation & database setup
- Week 6: Testing, monitoring, and refinement

### Dependencies
- Technology stack finalized (Phase 1)
- 16 URLs confirmed and accessible

### Success Criteria
- [ ] All 16 URLs successfully parsed daily
- [ ] 100% schema compliance for extracted data
- [ ] Data validation catches 100% of anomalies
- [ ] Scheduler runs reliably with 99%+ success rate
- [ ] Ingestion takes <30 minutes for all sources

---

## Phase 3: Knowledge Repository & Vector Storage (Weeks 7-11)

### Objectives
- Build hybrid knowledge repository (structured + vector)
- Implement embeddings pipeline
- Set up vector database
- Create fact verification and indexing layer

### Key Activities

#### 3.1 Structured Data Organization
- Create knowledge_repository directory structure
- Implement data loaders for PostgreSQL
- Build caching layer for frequently accessed data (Redis)
- Implement data versioning (track schema changes)
- Create backup and recovery procedures

#### 3.2 Embedding Pipeline
- **Embedding Model:** BAAI/bge-small-en-v1.5 (primary for local development; upgrade path: BAAI/bge-large-en-v1.5)
- **Chunking Strategy:**
  - Chunk size: 200-300 tokens
  - Overlap: 50-100 tokens
  - Preserve paragraph boundaries
- **Content to Embed:**
  - Scheme fact chunks (e.g., "HDFC Mid Cap Fund expense ratio is 0.95%")
  - Regulatory guidance text from AMFI/SEBI
  - FAQ-style answer snippets
  - Account statement process descriptions
- **Metadata Tagging:**
  ```json
  {
    "scheme_id": "hdfc-mid-cap-fund",
    "document_type": "scheme_facts",
    "source_url": "https://groww.in/...",
    "chunk_index": 1,
    "timestamp": "2026-06-01T00:00:00Z",
    "confidence_score": 0.95
  }
  ```

#### 3.3 Vector Database Setup (ChromaDB)
- Create ChromaDB collection with persistent storage
- Configure index parameters:
  - Similarity metric: Cosine similarity
  - Local storage: DuckDB + Parquet
  - Replication: local persistence with future cloud upgrade options
- Implement bulk upsert operations for daily updates
- Create indexing pipeline:
  1. Load structured data from PostgreSQL
  2. Generate embeddings for text chunks
  3. Upsert vectors to ChromaDB with metadata (documents, metadatas, ids)
  4. Verify collection health and query latency

#### 3.4 Hybrid Search Layer
- **Structured Search:**
  - Direct database queries for exact matches
  - SQL queries for scheme lookups
  - Cached results for popular queries
- **Vector Search:**
  - Query embedding generation
  - Similarity search in ChromaDB
  - Top-K retrieval (k=5-10)
  - Re-ranking by relevance
- **Search Ranking Algorithm:**
  ```python
  final_score = (
    0.35 * scheme_relevance +
    0.30 * source_authority +
    0.20 * recency_score +
    0.10 * confidence_score +
    0.05 * semantic_similarity
  )
  ```

#### 3.5 Fact Verification Layer
- Implement confidence scoring logic
- Build data provenance tracking
- Create fact update history (audit trail)
- Implement cross-source verification
- Build alert system for inconsistencies

#### 3.6 Data Organization
```
knowledge_repository/
├── structured_data/
│   ├── schemes.json         # All 10 HDFC schemes
│   ├── documents.json       # KIM, SID links
│   ├── regulatory_refs.json # AMFI/SEBI resources
│   └── fund_managers.json   # Fund manager profiles
├── vector_embeddings/
│   ├── scheme_facts.pkl     # Cached embeddings
│   ├── regulatory_guidance.pkl
│   └── faq_snippets.pkl
├── cache/
│   ├── popular_queries.json
│   └── search_results.cache
└── audit_trail/
    ├── data_changes.log
    ├── inconsistencies.log
    └── verification_report.json
```

### Deliverables
- [ ] Structured Data Organization & Caching
- [ ] Embedding Pipeline (model, chunking, vectorization)
- [ ] ChromaDB Vector Database Setup
- [ ] Hybrid Search Module (structured + vector)
- [ ] Fact Verification Engine
- [ ] Data Provenance & Audit Trail
- [ ] Knowledge Repository Documentation
- [ ] Storage Layer Tests (80%+ coverage)

### Timeline
- Week 7: Structured data org & embedding pipeline
- Week 8: Vector database setup & bulk ingestion
- Week 9: Hybrid search implementation & ranking
- Week 10: Fact verification layer & audit trails
- Week 11: Integration testing & optimization

### Dependencies
- Data ingestion pipeline completed (Phase 2)
- PostgreSQL database operational

### Success Criteria
- [ ] All scheme data loaded into PostgreSQL
- [ ] All content chunks embedded and indexed in ChromaDB
- [ ] Vector search latency <100ms (99th percentile)
- [ ] Hybrid search retrieves correct scheme facts
- [ ] Fact verification flags inconsistencies accurately
- [ ] Audit trail captures all data changes

---

## Phase 4: Query Processing & Retrieval Engine (Weeks 12-16)

### Objectives
- Build query classification pipeline
- Implement multi-stage retrieval strategy
- Create ambiguity handling logic
- Develop intent detection module

### Key Activities

#### 4.1 Query Preprocessing Module
- Text normalization (lowercase, punctuation removal)
- Tokenization and lemmatization
- Stop word removal
- Spell correction (using autocorrect library)
- PII detection (block queries containing PAN, Aadhaar, account numbers)

#### 4.2 Intent Classification Engine
- **Input:** Preprocessed query
- **Output:** Query type (FACTUAL / ADVISORY / AMBIGUOUS / OUT_OF_SCOPE)
- **Logic:**
  - Detect advisory keywords → ADVISORY (refuse)
  - Detect factual keywords → FACTUAL (proceed)
  - Detect out-of-scope topics → AMBIGUOUS (provide link)
  - Unclear intent → AMBIGUOUS (ask for clarification)
- **Advisory Keywords List:**
  ```python
  ADVISORY_KEYWORDS = [
    "should i invest", "which fund is better", "recommendation",
    "is this a good investment", "should i buy", "should i sell",
    "compare returns", "best performing", "highest returns",
    "guaranteed returns", "safe investment", "best fund"
  ]
  ```
- **Factual Keywords List:**
  ```python
  FACTUAL_KEYWORDS = [
    "expense ratio", "minimum investment", "exit load", "lock-in",
    "riskometer", "benchmark", "fund manager", "aum", "asset under management",
    "how to download", "capital gains", "statement", "tax certificate"
  ]
  ```

#### 4.3 Scheme & Fact Extraction Module
- Extract mentioned scheme names (fuzzy matching)
  - Handle variations: "Mid Cap", "HDFC Mid Cap Fund", "HDC Mid-Cap"
  - Use Levenshtein distance for fuzzy matching
- Extract fact types (e.g., "expense_ratio", "minimum_investment")
- Build query intent vector:
  ```json
  {
    "schemes": ["hdfc-mid-cap-fund"],
    "fact_types": ["expense_ratio", "minimum_investment"],
    "confidence": 0.95
  }
  ```

#### 4.4 Multi-Stage Retrieval Implementation

**Stage 1: Structured Data Retrieval**
- Query PostgreSQL for exact matches
- Lookup: scheme name → scheme_id
- Lookup: fact type → column query
- Return with high confidence

**Stage 2: Vector-Based Semantic Retrieval**
- Embed query into 384-dimensional space
- Search ChromaDB for similar chunks
- Retrieve top-10 results with similarity scores
- Filter by scheme relevance

**Stage 3: Hybrid Ranking & Selection**
- Apply ranking formula:
  ```
  final_score = 
    0.35 * scheme_relevance + 
    0.30 * source_authority + 
    0.20 * recency_score + 
    0.10 * confidence_score + 
    0.05 * semantic_similarity
  ```
- Select top-ranked chunk as primary source

#### 4.5 Ambiguity Handling Logic
- Multiple schemes matched → Request clarification
- Fact not in corpus → Suggest official source link
- Conflicting sources → Flag as ambiguous, provide all links
- Query too vague → Ask for more specifics

#### 4.6 Query Classification Tests
- Unit tests for each classifier
- Integration tests for full pipeline
- Edge case handling:
  - Typos and misspellings
  - Scheme name variations
  - Questions combining multiple facts
  - Questions about schemes not in corpus

### Deliverables
- [ ] Query Preprocessing Module
- [ ] Intent Classification Engine with keyword lists
- [ ] Scheme & Fact Extraction Module
- [ ] Multi-Stage Retrieval Pipeline (structured + vector)
- [ ] Hybrid Ranking Algorithm
- [ ] Ambiguity Handling Logic
- [ ] Query Processing Module Tests (85%+ coverage)
- [ ] Query Classification Validation Report

### Timeline
- Week 12: Query preprocessing & PII detection
- Week 13: Intent classification & fact extraction
- Week 14: Structured data retrieval & vector search
- Week 15: Hybrid ranking & ambiguity handling
- Week 16: Integration & end-to-end testing

### Dependencies
- Knowledge repository operational (Phase 3)
- PostgreSQL and ChromaDB populated with data

### Success Criteria
- [ ] PII queries blocked 100%
- [ ] Advisory queries correctly classified >98%
- [ ] Factual queries correctly classified >95%
- [ ] Relevant scheme facts retrieved in top-3 results >90%
- [ ] Query processing time <500ms per query
- [ ] Ambiguity handling provides helpful guidance

---

## Phase 5: Response Generation & Compliance Layer (Weeks 17-20)

### Objectives
- Implement answer generation logic
- Build compliance validation engine
- Create refusal handling module
- Enforce response formatting rules

### Key Activities

#### 5.1 Answer Generation Logic
- **Input:** Retrieved fact chunk + user query
- **Process:**
  1. Extract key data points from retrieved chunks
  2. Verify data against source document
  3. Compose 1-3 concise, factual sentences
  4. Use objective language (avoid recommendations)
  5. Quote numbers/data directly from sources
- **Output:** Factual answer string

#### 5.2 Citation Assignment Module
- Select one authoritative source URL from retrieved chunk
- Verify URL is valid and from curated corpus
- Preserve exact source link for user
- Store source metadata:
  ```json
  {
    "citation_link": "https://groww.in/...",
    "citation_text": "Groww - HDFC Mid Cap Fund",
    "source_authority": "Groww",
    "source_tier": 1
  }
  ```

#### 5.3 Response Formatting Engine
- **Response Template for Factual Answers:**
  ```json
  {
    "response_type": "FACTUAL",
    "response_text": "The HDFC Mid Cap Fund has an expense ratio of 0.95% for direct growth plans. The minimum investment is ₹5,000 for lump sum and ₹500 for SIP. You can view the complete scheme details in the factsheet.",
    "citation_link": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "citation_text": "Groww - HDFC Mid Cap Fund",
    "footer": "Last updated from sources: 2026-06-01",
    "timestamp": "2026-06-01T10:30:00Z",
    "confidence_score": 0.95
  }
  ```

- **Response Template for Refusal:**
  ```json
  {
    "response_type": "REFUSAL",
    "response_text": "I can only provide factual information about mutual fund schemes. I cannot recommend specific funds or make investment decisions. Please consult a qualified financial advisor for personalized investment advice.",
    "educational_link": "https://www.amfiindia.com/investor",
    "educational_link_text": "AMFI - How to Invest in Mutual Funds",
    "footer": "Last updated from sources: 2026-06-01",
    "timestamp": "2026-06-01T10:30:00Z"
  }
  ```

#### 5.4 Compliance Validation Rules
- **Rule 1:** No PII Collection
  - Check: Response doesn't ask for PAN, Aadhaar, account numbers, OTPs
  - Action: Reject response if PII requested
  
- **Rule 2:** No Performance Claims
  - Check: Response doesn't compare returns or predict performance
  - Action: Replace with link to official factsheet
  
- **Rule 3:** No Advisory Language
  - Keywords to remove: "should", "recommend", "best", "avoid"
  - Check: Scan response for advisory terms
  - Action: Remove or replace with factual language
  
- **Rule 4:** One Citation Only
  - Check: Exactly 1 citation link in response
  - Action: Error if multiple links detected
  
- **Rule 5:** Sentence Limit
  - Check: Response ≤ 3 sentences
  - Action: Truncate or combine sentences if needed
  
- **Rule 6:** Source Authenticity
  - Check: Citation link is in curated corpus
  - Action: Replace with valid source if not found
  
- **Rule 7:** Data Staleness
  - Check: Data used is <30 days old
  - Action: Flag warning if data older than threshold
  
- **Rule 8:** Refusal Polarity
  - Check: Refusal message uses polite, helpful tone
  - Action: Rewrite if tone is dismissive

#### 5.5 Regulatory Compliance Features
- **SEBI Compliance Module:**
  - No prediction of future returns
  - No comparison between schemes
  - No claim of guaranteed returns
  - Proper risk disclosure (include riskometer if available)
  
- **AMFI Code of Conduct Module:**
  - Verify all responses are factual and verifiable
  - Mandate source citations
  - Check for misleading information
  - Ensure disclaimer is visible
  
- **Privacy Compliance Module:**
  - Log queries anonymously (no IP, PII)
  - Audit trail for compliance reporting
  - Consent check for data processing

#### 5.6 Refusal Handling Module
- **Trigger:** Query classified as ADVISORY or OUT_OF_SCOPE
- **Refusal Types:**
  1. Investment Advice Refusal
  2. Out-of-Scope Refusal
  3. Ambiguous Query Refusal
- **Refusal Templates:**
  ```python
  REFUSAL_TEMPLATES = {
    "investment_advice": "I can only provide factual information about mutual fund schemes. I cannot recommend specific funds or make investment decisions. Please consult a qualified financial advisor for personalized investment advice.",
    "comparison": "I cannot compare fund performance or returns. Please visit the official factsheet or consult a financial advisor for detailed performance comparisons.",
    "out_of_scope": "I can only answer questions about HDFC mutual funds. For information about other providers, please visit their official websites.",
    "ambiguous": "Could you please clarify your question? Are you asking about [options]?"
  }
  ```
- **Educational Links to Provide:**
  - AMFI: https://www.amfiindia.com/investor
  - SEBI: https://investor.sebi.gov.in/understanding_mf.html
  - HDFC: https://www.hdfcfund.com/information/online-services-investors

#### 5.7 Testing & Validation
- Unit tests for each response rule
- Integration tests for full pipeline
- Compliance checklist validation
- Sample responses validated by legal/compliance team

### Deliverables
- [ ] Answer Generation Logic
- [ ] Citation Assignment Module
- [ ] Response Formatting Engine
- [ ] Compliance Validation Rules (8 rules implemented)
- [ ] Regulatory Compliance Features (SEBI, AMFI, Privacy)
- [ ] Refusal Handling Module
- [ ] Response Generation Tests (85%+ coverage)
- [ ] Compliance Validation Report

### Timeline
- Week 17: Answer generation & citation logic
- Week 18: Response formatting & validation rules
- Week 19: Regulatory compliance & refusal handling
- Week 20: Testing & compliance sign-off

### Dependencies
- Query retrieval engine operational (Phase 4)
- Legal/compliance team review of compliance rules

### Success Criteria
- [ ] 100% of responses include exactly 1 citation
- [ ] 100% of responses ≤ 3 sentences
- [ ] 100% of advisory queries result in polite refusal
- [ ] 0% of responses contain PII requests
- [ ] Compliance checklist 100% passed
- [ ] Legal team approves all response templates

---

## Phase 6: User Interface & Integration (Weeks 21-24)

### Objectives
- Build minimal, user-friendly web interface
- Integrate all backend components
- Implement end-to-end testing
- Deploy to staging environment

### Key Activities

#### 6.1 Frontend UI Design & Development

**UI Components:**
1. **Header Section**
   - Title: "HDFC Mutual Fund FAQ Assistant"
   - Disclaimer: "Facts-only. No investment advice."
   - Logo/branding

2. **Welcome Message Section**
   - Greeting text
   - Explanation of capabilities
   - List of answerable topics

3. **Example Questions Section**
   - 3 sample questions that show system capabilities
   - Clickable questions for easy interaction
   - Examples:
     1. "What is the expense ratio of HDFC Mid Cap Fund?"
     2. "What is the minimum SIP amount for HDFC Large Cap Fund?"
     3. "How do I download my capital gains certificate for HDFC funds?"

4. **Query Input Area**
   - Text input field with placeholder text
   - "Ask" button (or Enter to submit)
   - Character limit indicator (e.g., 500 chars)

5. **Response Display Area**
   - Response text (1-3 sentences)
   - Source link with icon and text
   - Footer with "Last updated from sources: YYYY-MM-DD"
   - Loading indicator while fetching response
   - Error message display if query fails

6. **Disclaimer Footer**
   - Full disclaimer text
   - Link to AMFI and SEBI resources
   - About and Contact links

**Technology Stack:**
- React 18 for component library
- Tailwind CSS for styling
- Axios for API calls
- React Query for state management
- Responsive design for mobile/tablet

#### 6.2 API Integration
- Create REST API endpoints:
  ```
  POST /api/v1/query
  Input: {
    "question": "What is the expense ratio of HDFC Mid Cap Fund?"
  }
  Output: {
    "response_type": "FACTUAL",
    "response_text": "...",
    "citation_link": "...",
    "citation_text": "...",
    "footer": "..."
  }
  
  GET /api/v1/health
  Output: {
    "status": "healthy",
    "version": "1.0.0"
  }
  ```

- Error handling for API failures
- Rate limiting (100 req/min per IP)
- Request validation and sanitization

#### 6.3 Backend API Development (FastAPI)
- Query endpoint implementation
- Response marshalling
- Error handling and logging
- Authentication (if needed)
- Rate limiting middleware
- CORS configuration for frontend

#### 6.4 Database Connection & Caching
- Connection pooling for PostgreSQL
- Redis caching for popular queries
- Cache invalidation strategy
- ChromaDB vector search integration

#### 6.5 Logging & Monitoring
- Query logging (anonymized)
- Response metrics (latency, success rate)
- Error logging with stack traces
- Audit trail logging
- CloudWatch/ELK integration

#### 6.6 End-to-End Testing
- Integration tests (all components together)
- User journey testing:
  1. User asks factual question → System returns accurate response
  2. User asks advisory question → System refuses politely
  3. User asks out-of-scope question → System provides link
  4. User clicks example question → System returns response
  5. User sees disclaimer and understands facts-only limitation
- Performance testing (latency, throughput)
- Load testing (concurrent users)
- Error scenario testing

#### 6.7 Staging Deployment
- Docker containerization
- Docker Compose for local dev environment
- AWS EC2 instance setup
- Environment configuration (dev, staging, prod)
- Database backup and recovery

#### 6.8 User Acceptance Testing (UAT)
- Coordinate with stakeholders (Groww, HDFC, product team)
- Test against 50+ query scenarios
- Gather feedback on UI/UX
- Refinements based on feedback
- Sign-off from stakeholders

### Deliverables
- [ ] React Frontend UI (fully functional)
- [ ] FastAPI Backend API
- [ ] Database Connection & Caching Layer
- [ ] End-to-End Integration Tests
- [ ] Staging Environment Setup
- [ ] Logging & Monitoring Infrastructure
- [ ] User Acceptance Testing Report
- [ ] Deployment Documentation

### Timeline
- Week 21: Frontend UI development
- Week 22: API development & integration
- Week 23: End-to-end testing & UAT
- Week 24: Staging deployment & refinements

### Dependencies
- All backend components operational (Phases 1-5)
- UI/UX design finalized
- Stakeholder availability for UAT

### Success Criteria
- [ ] Frontend UI responsive and intuitive
- [ ] All API endpoints functional
- [ ] End-to-end tests pass >95%
- [ ] User journey tests pass 100%
- [ ] Query latency <2 seconds (99th percentile)
- [ ] System handles 100+ concurrent users
- [ ] UAT sign-off from stakeholders
- [ ] Staging environment stable for 1 week

---

## Phase 7: Testing, Deployment & Go-Live (Weeks 25-28)

### Objectives
- Conduct comprehensive security & compliance testing
- Deploy to production
- Monitor system health
- Execute go-live plan

### Key Activities

#### 7.1 Security & Compliance Testing
- **Security Testing:**
  - OWASP Top 10 vulnerability scan
  - SQL injection testing
  - XSS (Cross-Site Scripting) testing
  - CSRF protection verification
  - SSL/TLS certificate validation
  - Rate limiting effectiveness
  - DDoS protection testing
  
- **Compliance Testing:**
  - SEBI compliance checklist validation
  - AMFI code of conduct verification
  - Data privacy compliance (PII handling)
  - Audit trail completeness
  - Disclaimer visibility on all pages

- **Data Quality Testing:**
  - Verify all 10 schemes in database
  - Verify all 16 sources accessible
  - Verify citation accuracy >99%
  - Verify fund data consistency
  - Verify freshness (daily updates)

#### 7.2 Performance & Load Testing
- **Metrics to Test:**
  - Query latency (target: <2s 99th percentile)
  - Throughput (target: 100+ req/sec)
  - Error rate (target: <0.1%)
  - Vector search latency (target: <100ms)
  - Database query time (target: <50ms)

- **Load Testing Scenarios:**
  - 100 concurrent users
  - 500 concurrent users
  - 1000 concurrent users
  - Sustained traffic for 24 hours

- **Tools:** Apache JMeter, Locust

#### 7.3 Production Environment Setup
- **Infrastructure:**
  - AWS EC2 instance (production grade)
  - Auto-scaling groups
  - Load balancer (ELB/ALB)
  - Multi-AZ deployment for high availability
  - RDS for PostgreSQL (automated backups)
  - ChromaDB production-ready deployment (with Pinecone as a future cloud alternative)

- **Configuration:**
  - Environment variables for production
  - SSL/TLS certificates
  - Domain name registration
  - CDN for static assets (CloudFront)
  - WAF (Web Application Firewall)

- **Backup & Recovery:**
  - Database backup schedule (hourly)
  - Point-in-time recovery
  - Disaster recovery plan
  - RTO (Recovery Time Objective): <1 hour
  - RPO (Recovery Point Objective): <15 minutes

#### 7.4 Deployment Strategy
- **Blue-Green Deployment:**
  - Deploy new version to green environment
  - Run smoke tests on green
  - Switch traffic from blue to green
  - Keep blue as rollback point for 2 hours
  - Rollback procedure documented

- **Rollout Plan:**
  - Day 1: Deploy to production (off-peak hours, 2 AM IST)
  - Day 1-2: Monitor system metrics closely
  - Day 2: Announce go-live to users
  - Days 3-7: Monitor for issues and user feedback

#### 7.5 Monitoring & Alerting Setup
- **Metrics to Monitor:**
  - System availability (uptime %)
  - Query success rate
  - API latency (p50, p95, p99)
  - Error rate
  - Database connection pool usage
  - Vector search latency
  - Cache hit rate
  - Ingestion success rate
  - CPU/Memory utilization

- **Alerting Thresholds:**
  - Downtime >5 minutes → Critical alert
  - Error rate >1% → Warning
  - Latency p99 >5 seconds → Warning
  - Ingestion failure → Critical alert
  - Database connection exhaustion → Critical alert

- **Tools:** CloudWatch, Datadog, or New Relic

#### 7.6 Support & Documentation
- **User Documentation:**
  - System overview
  - How to use the assistant
  - FAQ
  - Troubleshooting guide
  - Disclaimer and compliance info

- **Admin Documentation:**
  - Deployment guide
  - Monitoring guide
  - Backup/recovery procedures
  - Troubleshooting guide
  - Corpus management guide

- **Support Team Training:**
  - System walkthrough
  - Common issues and fixes
  - Escalation procedures
  - 24/7 on-call rotation

#### 7.7 Go-Live Execution
- **Pre-Launch Checklist:**
  - [ ] Security testing passed
  - [ ] Compliance testing passed
  - [ ] Load testing passed
  - [ ] Backups configured
  - [ ] Monitoring setup complete
  - [ ] Incident response plan ready
  - [ ] Support team trained
  - [ ] Documentation complete

- **Launch Day (T-0):**
  - 1 AM: Final backup
  - 2 AM: Deploy production
  - 2:15 AM: Smoke testing
  - 2:30 AM: Announce deployment
  - 2:30-4 AM: Monitor closely
  - 4-24 AM: Scheduled monitoring

- **Post-Launch (T+1 to T+7):**
  - Daily standup meetings
  - Monitor user feedback
  - Track metrics closely
  - Fix critical issues immediately
  - Plan Phase 2 enhancements

#### 7.8 Performance Optimization (if needed)
- Identify bottlenecks from monitoring
- Optimize slow queries
- Add caching layer
- Scale horizontally if needed
- Refactor inefficient code

### Deliverables
- [ ] Security & Compliance Test Report
- [ ] Performance & Load Test Report
- [ ] Production Environment Fully Configured
- [ ] Deployment Runbook
- [ ] Monitoring & Alerting Dashboard
- [ ] User & Admin Documentation
- [ ] Incident Response Playbook
- [ ] Go-Live Checklist & Sign-Off
- [ ] Post-Launch Monitoring Report (1 week)

### Timeline
- Week 25: Security & compliance testing
- Week 26: Performance & load testing
- Week 27: Production setup & deployment prep
- Week 28: Deployment & go-live execution

### Dependencies
- Staging environment stable (Phase 6)
- Infrastructure provisioned
- Support team trained
- Legal/compliance team sign-off

### Success Criteria
- [ ] Security audit passes with 0 critical findings
- [ ] Compliance audit passes 100%
- [ ] System handles target load without degradation
- [ ] Query latency <2 seconds (99th percentile)
- [ ] System uptime >99.5% in first week
- [ ] Error rate <0.1%
- [ ] User feedback positive
- [ ] Stakeholder go-live approval

---

## Phase 2+ Enhancement Roadmap (After Go-Live)

### Phase 8: Post-Launch Monitoring & Optimization (Weeks 29-32)
- Monitor production metrics for 4 weeks
- Identify and fix performance issues
- Refine answer generation based on user queries
- Gather user feedback for Phase 2

### Phase 9: Phase 2 Enhancements (Q3 2026)
- [ ] Extend corpus to 3-5 additional AMCs
- [ ] Implement real-time NAV integration
- [ ] Add multi-language support (Hindi, Marathi)
- [ ] Build admin dashboard for corpus management
- [ ] Implement feedback loop for answer refinement

### Phase 10: Advanced Features (Q4 2026 - 2027)
- [ ] Advanced search filters (scheme category, risk level)
- [ ] Analytics dashboard (query trends, coverage)
- [ ] Voice query support
- [ ] Recommendation engine (facts-only suggestions)
- [ ] Portfolio analysis integration

---

## Resource Planning

### Team Composition
- **1x Project Manager:** Overall coordination, stakeholder management
- **2x Backend Developers:** Data pipeline, retrieval engine, API
- **1x Data Engineer:** Data ingestion, ETL, vector database
- **1x Frontend Developer:** UI/UX implementation
- **1x QA Engineer:** Testing, quality assurance
- **1x DevOps Engineer:** Infrastructure, deployment, monitoring

### Tools & Licenses
- GitHub (free for open source, or paid for private)
- ChromaDB (local persistent store) or Pinecone (production cloud alternative)
- AWS (EC2, RDS, CloudWatch)
- PostgreSQL (free, open source)
- Python frameworks (FastAPI, etc. - free, open source)
- React (free, open source)

### Budget Estimate
- Cloud infrastructure (AWS): $2,000-5,000/month
- Vector database (ChromaDB local; Pinecone production option): $0-$2,000/month
- Developer tools & licenses: $500-1,000/month
- **Total monthly:** ~$3,500-8,000/month
- **6-month project cost:** ~$21,000-48,000 + team salaries

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Data source URLs become inaccessible | Medium | High | Implement URL health checks, build fallback mechanisms |
| Vector search returns irrelevant results | Medium | Medium | Fine-tune embeddings, improve chunking strategy |
| Regulatory compliance requirements change | Low | High | Build compliance layer as separate module, easy to update |
| Performance issues at scale | Medium | High | Load testing early, optimize database queries |
| Data quality issues (stale/incorrect data) | Medium | Medium | Implement fact verification layer, daily audit reports |
| Integration failures between components | Medium | High | Comprehensive integration testing, CI/CD pipeline |
| Security vulnerabilities discovered | Low | Critical | Regular security audits, penetration testing |

---

## Success Metrics

### Functional Metrics
- [ ] All 16 URLs successfully ingested daily
- [ ] >95% accuracy on factual queries
- [ ] >98% accuracy on advisory query refusal
- [ ] 100% citation link validity
- [ ] >99% uptime in production

### Performance Metrics
- [ ] Query response time <2 seconds (99th percentile)
- [ ] System handles 100+ concurrent users
- [ ] Vector search latency <100ms
- [ ] Database query time <50ms
- [ ] Cache hit rate >70%

### User Metrics
- [ ] >90% user satisfaction score
- [ ] >80% of example questions lead to resolution
- [ ] <2% error rate reported by users
- [ ] High engagement with factual queries

### Business Metrics
- [ ] Reduces customer support volume by >30%
- [ ] Positive ROI within 6 months
- [ ] User adoption >60% among target audience
- [ ] Zero regulatory complaints

---

## Summary

This phased implementation plan provides a structured approach to building the Mutual Fund FAQ Assistant over 28 weeks. Each phase builds on the previous one, with clear deliverables, success criteria, and risk mitigation strategies. The plan emphasizes data quality, regulatory compliance, and user experience, ensuring a trustworthy, accurate, and compliant system.

**Key Success Factors:**
1. Strong data governance and fact verification
2. Strict compliance with SEBI/AMFI regulations
3. Comprehensive testing at each phase
4. Continuous monitoring and optimization
5. Clear stakeholder communication and alignment
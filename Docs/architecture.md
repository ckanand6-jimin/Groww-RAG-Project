# Architecture Overview - Mutual Fund FAQ Assistant

## Executive Summary
The Mutual Fund FAQ Assistant is a compliance-focused, lightweight Retrieval-Augmented Generation (RAG) system designed to deliver accurate, source-backed factual information about HDFC mutual fund schemes. The system prioritizes data accuracy, regulatory compliance, and user trust through strict facts-only responses, mandatory source citations, and controlled refusal behavior for advisory queries.

**Technology Stack:** Python/Node.js backend, LLM-based retrieval with semantic search, vector database for corpus storage, minimal web/chat UI

**Primary Use Cases:** 
- Retail investor self-service FAQ
- Customer support agent knowledge base
- Content team reference tool

---

## System Architecture - Layered Design

### Layer 1: Data Ingestion & Corpus Management

#### 1.1 Source Collection
The system ingests data from 16 curated official sources organized in three tiers:

**Tier 1 - Groww Platform (10 URLs)**
- Scheme-level pages for 10 HDFC funds
- Provides:
  - Current expense ratios and fund details
  - Minimum investment amounts (lump sum & SIP)
  - Exit load structures and lock-in periods
  - Riskometer classifications
  - Fund manager information and fund history
  - Real-time AUM data
  - Direct purchase/redemption process links

**Tier 2 - HDFC Official (4 URLs)**
- Key Information Memorandum (KIM): Legal document with scheme objectives, risk profile, and investment strategy
- Scheme Information Document (SID): Detailed regulatory document with features, benefits, and terms
- Investor Online Services: Account management, statement downloads, transaction guides
- Consolidated Account Statement Services: Tax document (Capital Gains Certificate) generation, PAN linking process

**Tier 3 - Regulatory Bodies (2 URLs)**
- AMFI Investor Hub: Mutual fund basics, investor education, rights and responsibilities
- SEBI Investor Portal: Market regulations, MF education modules, grievance procedures

#### 1.2 Data Extraction Strategy
- **Web Scraping Module:** Automated extraction of structured data from URLs
- **Parser Pipeline:** 
  - HTML to structured data conversion
  - Text normalization and tokenization
  - Metadata extraction (scheme name, fund manager, inception date, AUM)
  - Link preservation for source citations
- **Validation Layer:** Cross-reference extracted data against official sources to ensure accuracy
- **Scheduler:** A daily scheduler triggers the ingestion component automatically each day
- **Update Frequency:** Daily/Weekly corpus refresh to capture scheme updates (expense ratios, AUM, fund manager changes)

#### 1.3 Data Schema Design
```
FUND_SCHEME {
  scheme_id: "hdfc-mid-cap-fund"
  scheme_name: "HDFC Mid Cap Fund"
  scheme_type: "Equity | Debt | Hybrid | ELSS"
  category: "Equity > Mid Cap" | "Debt > Liquid" | etc.
  
  financial_data: {
    expense_ratio: "0.95%" | numeric
    minimum_investment_lump_sum: "₹5,000" | numeric (in paise)
    minimum_investment_sip: "₹500" | numeric (in paise)
    current_aum: "₹15,432 Cr" | numeric (in paise)
    inception_date: "YYYY-MM-DD"
    fund_age_years: numeric
  }
  
  risk_return: {
    riskometer_class: "Low" | "Low-Moderate" | "Moderate" | "Moderate-High" | "High"
    benchmark_index: "NSE Nifty 500" | "BSE Sensex" | etc.
    portfolio_type: "Large Cap" | "Mid Cap" | "Small Cap" | "Balanced" | etc.
  }
  
  management: {
    fund_manager_name: string
    fund_manager_experience_years: numeric
    co_fund_manager_name: string | null
    fund_manager_tenure_with_scheme: string
  }
  
  exit_details: {
    exit_load_percentage: "1.0%" | numeric
    exit_load_applicability: "Up to 1 year" | string
    lock_in_period_days: numeric | null
    elss_lock_in_years: numeric | null (if ELSS)
  }
  
  documents: {
    kim_link: "https://www.hdfcfund.com/investor-services/fund-documents/kim"
    sid_link: "https://www.hdfcfund.com/investor-services/fund-documents/sid"
    factsheet_link: string
    prospectus_link: string
  }
  
  account_services: {
    statement_download_link: string
    statement_frequency: "Monthly" | "Quarterly" | "Annual"
    capital_gains_cert_availability: boolean
    account_statement_process: string (detailed steps)
    online_services_link: string
  }
  
  sources: {
    groww_url: "https://groww.in/..."
    hdfc_official_url: "https://www.hdfcfund.com/..."
    last_updated: "YYYY-MM-DD HH:MM:SS"
    data_version: numeric
  }
}

QUERY_INTENT {
  query_id: unique_string
  original_query: string
  query_type: "FACTUAL" | "ADVISORY" | "AMBIGUOUS"
  intent: "expense_ratio" | "minimum_investment" | "exit_load" | "riskometer" | "benchmark" | "fund_manager" | "aum" | "account_statement" | "tax_document" | etc.
  schemes_mentioned: [scheme_ids]
  confidence_score: 0.0 - 1.0
}

RESPONSE {
  response_id: unique_string
  query_id: reference
  response_type: "FACTUAL" | "REFUSAL"
  response_text: string (max 3 sentences)
  citation_link: string (exactly one URL from corpus)
  citation_text: string (source name)
  footer: "Last updated from sources: YYYY-MM-DD"
  timestamp: "YYYY-MM-DD HH:MM:SS"
  confidence_score: 0.0 - 1.0
}
```

---

### Layer 2: Knowledge Repository & Vector Storage

#### 2.1 Knowledge Base Architecture
- **Storage Type:** Hybrid approach combining structured and vector storage
  - **Structured Storage:** PostgreSQL/SQLite for fund metadata (expense ratio, AUM, fund manager)
  - **Vector Database:** ChromaDB (local persistent store) for semantic search on unstructured corpus content; Pinecone/Weaviate/Milvus listed as production-scale alternatives
  - **Document Store:** JSON/JSONL files for scheme factsheets and reference documents

#### 2.2 Embedding Strategy
- **Embedding Model:** BAAI/bge-small-en-v1.5 (primary for local development). Upgrade path: BAAI/bge-large-en-v1.5 for production-quality embeddings.
- **Chunking Strategy:**
  - Chunk size: 200-300 tokens per chunk
  - Overlap: 50-100 tokens to preserve context
  - Chunks tagged with metadata: {scheme_id, document_type, source_url}
- **Indexing:** Build vector indices for:
  - Scheme-specific fact chunks
  - Regulatory guidance text
  - FAQ answer snippets

#### 2.3 Data Organization
```
knowledge_repository/
├── structured_data/
│   ├── schemes.json         # All 10 HDFC schemes metadata
│   ├── documents.json       # KIM, SID, official links
│   ├── regulatory_refs.json # AMFI & SEBI resource links
│   └── fund_managers.json   # Fund manager profiles
├── vector_indices/
│   ├── scheme_facts.index      # Vectors for scheme-specific data
│   ├── regulatory_guidance.index
│   └── faq_snippets.index
├── raw_documents/
│   ├── groww_pages/         # Cached/parsed Groww pages
│   ├── hdfc_documents/      # KIM, SID content
│   └── regulatory_content/  # AMFI/SEBI resources
└── corpus_metadata.json     # Index of all sources + timestamps
```

#### 2.4 Fact Verification Layer
- For each fund fact in the knowledge base:
  - Source URL reference (primary source)
  - Cross-reference verification (checked against 2+ official sources if available)
  - Last verified date
  - Confidence flag (High/Medium/Low)
- Automated alerts for data inconsistencies across sources

---

### Layer 3: Query Processing & Retrieval Engine

#### 3.1 Query Classification Pipeline
```
Input Query
    ↓
[Pre-processing: lowercase, remove punctuation, tokenize]
    ↓
[Intent Detection Module]
    - Extract scheme names (fuzzy matching against known schemes)
    - Extract fact types (expense ratio, exit load, fund manager, etc.)
    - Identify query intent from {FACTUAL, ADVISORY, AMBIGUOUS, OUT_OF_SCOPE}
    ↓
[Query Type Classifier]
    - If advisory keywords detected → ADVISORY (refuse)
    - If out-of-scope → AMBIGUOUS (provide link)
    - If factual intent clear → FACTUAL (proceed to retrieval)
```

**Advisory Query Keywords (Refusal Triggers):**
- "Should I invest", "Which fund is better", "What is your recommendation", "Is this a good investment", "Should I buy/sell", "Compare returns", "Best performing fund", etc.

**Factual Query Keywords (Retrieval Triggers):**
- "What is the expense ratio", "What is the minimum investment", "What are the exit loads", "What is the riskometer", "What is the benchmark", "Who is the fund manager", "What is the lock-in period", "How do I download statement", "What is the capital gains certificate", etc.

#### 3.2 Multi-Stage Retrieval Strategy

**Stage 1: Structured Data Retrieval**
- Query database for exact matches:
  - Scheme name lookup (handle variations: "HDFC Mid Cap", "Mid Cap Fund")
  - Fact attribute lookup (expense_ratio, aum, fund_manager, etc.)
- Return structured results with high confidence

**Stage 2: Vector-Based Semantic Retrieval**
- Embed the user query into 384-dimensional vector space
- Perform similarity search in vector database
- Retrieve top-K chunks (k=5-10) with similarity scores
- Filter by scheme relevance and document type

**Stage 3: Hybrid Ranking & Selection**
```
Ranking Criteria:
1. Scheme Relevance (exact match scheme > partial match > general scheme info)
2. Source Authority (HDFC official > Groww > AMFI/SEBI)
3. Recency (more recent updates ranked higher)
4. Confidence Score (high-confidence facts preferred)
5. Semantic Similarity Score (from vector search)

Final Score = 
  (0.35 × scheme_relevance) + 
  (0.30 × source_authority) + 
  (0.20 × recency_score) + 
  (0.10 × confidence_score) + 
  (0.05 × semantic_similarity)
```

- Select top-ranked chunk as primary source for answer generation

#### 3.3 Ambiguity Handling
- If query matches multiple schemes → Ask for clarification or return general guidance
- If query fact is not in corpus → Provide link to official source for user to verify
- If multiple conflicting sources found → Flag as ambiguous and provide all relevant links

---

### Layer 4: Response Generation & Compliance Layer

#### 4.1 Answer Generation Logic
```
Retrieved Fact + User Query
    ↓
[Fact Extraction]
    - Extract key data points from retrieved chunks
    - Verify against source document
    ↓
[Response Composition]
    - Write 1-3 concise, factual sentences
    - Use objective language (avoid recommendations)
    - Quote numbers/data directly from sources
    ↓
[Citation Assignment]
    - Select one authoritative source URL
    - Preserve exact source link from corpus
    ↓
[Compliance Validation]
    - Check: Response ≤ 3 sentences
    - Check: Exactly 1 citation link
    - Check: No advisory language
    - Check: Include footer with date
    ↓
[Response Formatting]
    - Output format: JSON with response_text, citation_link, footer
```

#### 4.2 Response Template Examples

**Factual Response Format:**
```
"response_text": "The HDFC Mid Cap Fund has an expense ratio of 0.95% for direct growth plans. 
The minimum investment is ₹5,000 for lump sum and ₹500 for SIP. 
You can view the complete scheme details in the factsheet."

"citation_link": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
"citation_text": "Groww - HDFC Mid Cap Fund"

"footer": "Last updated from sources: 2026-06-01"
```

**Refusal Response Format:**
```
"response_type": "REFUSAL"
"response_text": "I can only provide factual information about mutual fund schemes. 
I cannot recommend specific funds or make investment decisions. 
Please consult a qualified financial advisor for personalized investment advice."

"educational_link": "https://www.amfiindia.com/investor"
"educational_link_text": "AMFI - How to Invest in Mutual Funds"

"footer": "Last updated from sources: 2026-06-01"
```

#### 4.3 Compliance & Safety Rules
- **Rule 1:** No PII Collection - System blocks queries asking for PAN, Aadhaar, account numbers, OTPs, email, phone
- **Rule 2:** No Performance Claims - Refuse queries asking to compare returns or predict performance
- **Rule 3:** No Advisory Language - Remove any recommendatory language from responses
- **Rule 4:** One Citation Only - Enforce exactly one source link per response
- **Rule 5:** Sentence Limit - Enforce maximum 3 sentences per response
- **Rule 6:** Source Authenticity - Validate all citations against the curated corpus
- **Rule 7:** Data Staleness Check - Flag responses using data > 30 days old
- **Rule 8:** Refusal Polarity - Use polite, helpful tone in refusal messages

#### 4.4 Regulatory Compliance Features
- **SEBI Compliance:**
  - No prediction of future returns
  - No comparison between schemes
  - No claim of guaranteed returns
  - Proper risk disclosure (riskometer classification included)
  
- **AMFI Code of Conduct:**
  - All responses factual and verifiable
  - Source citations mandatory
  - No misleading information
  - Disclaimer visible on every interaction

- **Privacy Compliance:**
  - No data collection beyond query logs (anonymized)
  - No PII processing
  - Audit trail for compliance reporting

---

### Layer 5: User Interface

#### 5.1 Interface Components

**Header Section:**
```
┌─────────────────────────────────────────────────────────┐
│  HDFC Mutual Fund FAQ Assistant                          │
│  ⓘ Facts-only. No investment advice.                    │
└─────────────────────────────────────────────────────────┘
```

**Welcome Message:**
```
Welcome! I can help you find factual information about HDFC mutual fund schemes.
I can answer questions about:
• Expense ratios and fees
• Minimum investment amounts
• Exit loads and lock-in periods
• Fund manager details
• How to download statements and tax documents
```

**Example Questions Section:**
```
Quick Example Questions:
1. "What is the expense ratio of HDFC Mid Cap Fund?"
2. "What is the minimum SIP amount for HDFC Large Cap Fund?"
3. "How do I download my capital gains certificate for HDFC funds?"
```

**Query Input Area:**
```
[Type your question here... ] [Ask]
```

**Response Display Area:**
```
Response:
─────────────────────────────────────────────
The HDFC Mid Cap Fund has an expense ratio of 0.95% for direct growth plans.
The minimum investment is ₹5,000 for lump sum and ₹500 for SIP.
You can view the complete scheme details in the factsheet.

📎 Source: Groww - HDFC Mid Cap Fund
   https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth

Last updated from sources: 2026-06-01
─────────────────────────────────────────────
```

**Disclaimer Footer:**
```
┌─────────────────────────────────────────────────────────┐
│ DISCLAIMER: This assistant provides facts-only          │
│ information. It does not provide investment advice,     │
│ recommendations, or financial guidance. Please consult  │
│ a qualified financial advisor before making investment  │
│ decisions.                                              │
└─────────────────────────────────────────────────────────┘
```

#### 5.2 Technical Stack Options
- **Frontend:**
  - Option A: React/Vue.js + Tailwind CSS (web UI)
  - Option B: Streamlit (rapid prototyping)
  - Option C: HTML + plain JavaScript (minimal)
  
- **Backend:**
  - Python FastAPI or Flask for API endpoints
  - Node.js Express as alternative
  
- **Deployment:**
  - Docker containerization
  - AWS EC2 / Azure App Service / Vercel

---

## Data Flow - End-to-End Workflow

```
USER QUERY
    ↓
[Input Validation]
    - Check for PII keywords (reject if found)
    - Check query length (typically 5-100 words)
    ↓
[Query Preprocessing]
    - Tokenize and normalize
    - Remove stop words
    - Spell correction
    ↓
[Intent Classification]
    - Classify as FACTUAL / ADVISORY / AMBIGUOUS / OUT_OF_SCOPE
    ↓
   ├─→ ADVISORY → [Refusal Module] → Polite refusal + educational link
   ├─→ OUT_OF_SCOPE → [Link Provider] → Relevant AMFI/SEBI link
   ├─→ AMBIGUOUS → [Clarification] → Ask for more specifics
    ↓
[FACTUAL QUERY PROCESSING]
    ↓
[Scheme & Fact Extraction]
    - Extract mentioned schemes
    - Extract fact types
    ↓
[Structured Data Lookup]
    - Query database for exact matches
    ↓
[Vector Search (if needed)]
    - Embed query into vector space
    - Search vector database
    - Retrieve top-K relevant chunks
    ↓
[Hybrid Ranking & Selection]
    - Apply ranking criteria
    - Select best source chunk
    ↓
[Response Composition]
    - Write factual answer (1-3 sentences)
    - Assign exact citation link
    ↓
[Compliance Validation]
    - Validate sentence count, citation, language
    ↓
[Response Formatting]
    - Structure response JSON
    - Add footer with timestamp
    ↓
FORMATTED RESPONSE TO USER
    ↓
[Logging & Audit]
    - Log query, response, timestamp
    - Track success/failure rates
```

---

## Detailed Fund Management Data - Retrieval Specification

**For Each Query, System Must Be Able to Retrieve:**

| Data Point | Source | Format | Example |
|-----------|--------|--------|---------|
| Scheme Name & Type | Groww, HDFC | Text | HDFC Mid Cap Fund - Equity |
| Expense Ratio | Groww, HDFC KIM | Percentage | 0.95% |
| Minimum Lump Sum | Groww, HDFC | Currency | ₹5,000 |
| Minimum SIP | Groww, HDFC | Currency | ₹500 |
| Exit Load | HDFC SID, Groww | Percentage + Duration | 1.0% up to 1 year |
| Lock-in Period | HDFC SID | Days/Years | 3 years (for ELSS) |
| Riskometer | Groww, HDFC | Category | Moderate |
| Benchmark Index | HDFC, Groww | Text | NSE Nifty 500 |
| Fund Manager Name | Groww, HDFC | Text | John Doe |
| Fund Manager Exp | HDFC | Years | 15 years |
| Fund Manager Tenure | HDFC, Groww | Duration | 3 years with this scheme |
| AUM | Groww | Currency in Cr | ₹15,432 Cr |
| Category | HDFC, Groww | Text | Equity > Mid Cap |
| Inception Date | HDFC, Groww | Date | 2010-03-15 |
| Fund Age | Calculated | Years | 16 years |
| KIM Link | HDFC | URL | https://www.hdfcfund.com/... |
| SID Link | HDFC | URL | https://www.hdfcfund.com/... |
| Statement Download | HDFC | URL + Steps | https://www.hdfcfund.com/services/... |
| Capital Gains Cert | HDFC | URL + Process | Download via Investor portal |

---

## Known Limitations & Constraints

1. **Corpus-Bound:** Can only answer questions on topics covered in the 16 curated sources
2. **Scheme Scope:** Limited to 10 HDFC schemes; cannot provide info on other AMCs unless corpus is expanded
3. **Real-Time Data:** Stock price/NAV updates require real-time integration (not in current scope)
4. **Performance Data:** Cannot retrieve historical returns or performance comparisons
5. **Personalization:** System is stateless; cannot personalize based on user profile
6. **Multi-Language:** Current version English-only; multi-language support requires additional embedding models
7. **Source Updates:** Depends on regular corpus refresh; stale data if sources not updated timely
8. **Semantic Precision:** Vector search may return false positives if query is very different from training corpus

---

## Future Enhancement Roadmap

### Phase 2 (Q3 2026)
- Extend corpus to 3-5 additional AMCs
- Implement real-time NAV integration
- Add multi-language support (Hindi, Marathi)
- Build admin dashboard for corpus management

### Phase 3 (Q4 2026)
- Add advanced search filters (scheme category, risk level)
- Implement feedback loop for answer refinement
- Build analytics dashboard (query trends, coverage analysis)
- Add voice query support

### Phase 4 (2027)
- Integrate with portfolio analysis tools
- Build recommendation engine (facts-only suggestions)
- Expand to international funds

---

## Security & Privacy Considerations

**Data Security:**
- All corpus sources use HTTPS
- Vector database encrypted at rest
- Query logs anonymized (no IP logging)
- Regular security audits of source links

**Privacy Protection:**
- System explicitly rejects PII queries
- No user profiling or tracking
- Compliance with Indian Data Protection Act
- Regular privacy impact assessments

**Access Control:**
- Admin access to corpus management restricted
- Query logging for compliance audit trail
- Rate limiting to prevent abuse

---

## Monitoring & Maintenance

**Health Checks:**
- Daily corpus freshness validation (check if URLs are live)
- Weekly consistency checks (cross-reference data across sources)
- Monthly compliance audit (refusal handling, citation accuracy)
- Quarterly user satisfaction surveys

**Alerting:**
- Alert if source URL returns 404/403
- Alert if expense ratio changes > 0.1%
- Alert if fund manager changes
- Alert if query success rate drops below 85%

**Metrics to Track:**
- Query volume and types
- Response accuracy (manual sample reviews)
- Refusal accuracy (ensuring advisory queries are caught)
- Citation link validity (daily checks)
- Average response time (target: <2 seconds)
- User satisfaction scores

---

## Summary

This detailed architecture ensures that the Mutual Fund FAQ Assistant operates as a reliable, compliant, facts-only information system. By combining curated official sources, strict validation rules, and user-friendly interface design, the system prioritizes accuracy and regulatory compliance over conversational naturalness.

## Data Flow

1. User submits a query via the interface.
2. The retrieval engine classifies the query as factual or advisory.
3. If factual:
   - The engine searches the knowledge repository for matching scheme data.
   - It selects the most relevant source document and verifies the answer.
   - The generator produces a short, citation-backed response.
4. If advisory or ambiguous:
   - The system returns a polite refusal with a relevant educational link.

## Source Corpus

### Groww - HDFC Funds (10 Schemes)
- hdfc-mid-cap-fund-direct-growth
- hdfc-large-cap-fund-direct-growth
- hdfc-small-cap-fund-direct-growth
- hdfc-equity-fund-direct-growth
- hdfc-elss-tax-saver-fund-direct-plan-growth
- hdfc-balanced-advantage-fund-direct-growth
- hdfc-nifty-50-index-fund-direct-growth
- hdfc-defence-fund-direct-growth
- hdfc-gold-etf-fund-of-fund-direct-plan-growth
- hdfc-liquid-fund-direct-growth

### HDFC Official Sources
- KIM documents
- SID documents
- Investor online services
- Consolidated account statement services

### AMFI & SEBI Resources
- Investor education hub
- Mutual fund understanding guide

## Response Constraints
- Only factual information from official sources may be used.
- No advice, recommendations, or performance comparisons.
- No user personal data may be requested or stored.
- For performance-related queries, return an official factsheet link only.

## Refusal Handling
- Identify advisory queries such as:
  - "Should I invest in this fund?"
  - "Which fund is better?"
- Respond politely with a facts-only refusal.
- Provide a relevant regulatory or investor education link.

## Implementation Considerations

### Retrieval Strategy
- Use phrase and keyword matching on scheme-specific facts.
- Prefer direct official links for citations.
- If multiple sources match, choose the most authoritative official source.

### Answer Validation
- Ensure each reply includes one citation.
- Include a clear source footer with a last-updated date.
- Keep answers short and strictly factual.

### UI Design
- Use a clean, minimal layout.
- Include:
  - Welcome message
  - Example questions
  - Disclaimer statement
  - Response area with citation

## Known Limitations
- The assistant cannot provide investment advice.
- It can only answer questions covered by the curated source corpus.
- It may not respond accurately to queries outside the selected HDFC funds.
- It depends on the corpus being current and correctly parsed.

## Future Enhancements
- Add more official scheme page sources for broader coverage.
- Implement automated periodic source updates.
- Extend the corpus to additional AMCs while preserving facts-only behavior.
- Add richer document linking for KIM/SID and regulatory updates.

## Summary
This architecture supports a compliance-focused, facts-only mutual fund FAQ assistant. It centers on official source retrieval, short citation-backed answers, and strict refusal behavior for advisory requests.
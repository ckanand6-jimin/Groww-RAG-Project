# Edge Cases and Corner Scenarios

This document lists edge cases and corner-case scenarios for the Mutual Fund FAQ Assistant, based on `architecture.md` and `implementation-plan-v2.md`.

## 1. Corpus & Ingestion

### 1.1 Source Accessibility
- A source URL returns 404/410/500 or times out.
- Page structure changes on Groww or HDFC sites, breaking the scraper.
- HDFC KIM/SID links are temporarily unavailable or moved.
- Regulatory pages have dynamic content or require JavaScript.
- Source pages contain hidden or truncated text.

### 1.2 Incomplete or Inconsistent Data
- Some pages omit fields such as expense ratio, benchmark index, or fund manager.
- SIP minimum is missing but lump sum minimum exists.
- Exit load details are described in prose rather than a structured table.
- Lock-in period is present only for ELSS and absent for other schemes.
- Fund manager information includes multiple names or interim managers.
- AUM is provided in different units or formats.

### 1.3 Data Quality and Validation
- Numeric values include commas, currency symbols, or text annotations.
- Fields appear as ranges instead of exact values.
- Conflicting information between Groww and HDFC official sources.
- Document parsers incorrectly merge adjacent sections.
- Duplicate or repeated scheme entries in parsed output.
- Date formats vary across sources.

### 1.4 Parsing and Schema Failures
- Parsed JSON fails schema validation due to missing required fields.
- Unexpected HTML structure leads to empty or malformed text chunks.
- Content metadata is missing source URL or scheme ID.
- Text chunking breaks on short or extremely long paragraphs.

## 2. Chunking & Embeddings

### 2.1 Chunk Content Issues
- Very short chunks lack enough context for retrieval.
- Very long chunks include unrelated nearby facts.
- Chunks split a meaningful fact across boundaries.
- Regulatory guidance text is too generic and returns low relevance.

### 2.2 Embedding Problems
- Embedding generation fails due to model input limits.
- Identical text chunks generate similar embeddings and confuse retrieval.
- Embeddings stored without proper metadata.
- Embedding model service becomes unavailable or rate-limited.

### 2.3 Metadata and Tagging
- Scheme IDs are inconsistent across chunks.
- Source URL or document type metadata is lost during storage.
- Chunk timestamps are missing or stale.

## 3. Vector Database & Retrieval

### 3.1 Search Failures
- Query embeddings return no results.
- Top-K results are irrelevant or from the wrong scheme.
- Retrieval returns duplicate chunks.
- Similarity scores are skewed by stop words or query noise.

### 3.2 Ranking and Relevance
- Official source documents rank lower than less-authoritative text.
- Recent updates are not prioritized due to stale recency scoring.
- Retrieval selects a chunk with a correct keyword but wrong fact.
- Ambiguous scheme names map to the wrong HDFC fund.

### 3.3 Storage and Load
- Vector store becomes inconsistent after failed upsert operations.
- Retrieval latency spikes during large corpus refresh.
- Local ChromaDB persistence load fails or becomes corrupted.

## 4. RAG Orchestrator

### 4.1 Response Assembly
- Retrieved chunk contains multiple facts and the response includes unrelated details.
- The response falls outside the 3-sentence limit.
- The answer misses the exact requested fact type.
- The response includes more than one citation or none.
- The footer date is missing or incorrectly formatted.

### 4.2 Source Assignment
- The orchestrator chooses a source link that is not part of the curated corpus.
- Citation link points to an intermediate page rather than the actual source.
- The selected chunk contains a summary line without a verifiable source.

### 4.3 Data Staleness
- The system uses outdated facts that are older than 30 days.
- Fresh data exists but is not reflected because embeddings/corpus were not refreshed.

## 5. Query Classification & Refusal Handling

### 5.1 Advisory Detection
- Advisory queries are phrased indirectly, e.g. “Should I put money into this fund?”
- Mixed queries contain a factual question and a recommendation request in the same sentence.
- Synonyms or local terms are used for advisory language.

### 5.2 False Positives / Negatives
- A factual query is mistakenly classified as advisory and refused.
- An advisory query slips through and proceeds to retrieval.
- Ambiguous queries are classified as factual due to keyword overlap.

### 5.3 Refusal Output
- Refusal responses include advisory tone or recommendation-like wording.
- Refusal message omits the educational link or footer.
- The refusal fails to clearly explain the facts-only limitation.

### 5.4 PII and Sensitive Data
- Query asks for PAN, Aadhaar, account number, OTP, email, or phone.
- Query includes partial personal data patterns that are mistaken for factual requests.
- System logs sensitive query content unexpectedly.

## 6. Scheduler & Corpus Refresh

### 6.1 Scheduling Issues
- Daily scheduler fails to start or crashes silently.
- Multiple scheduler instances run concurrently and conflict.
- Scheduled job runs overlap due to long ingestion time.

### 6.2 Refresh Failures
- Corpus refresh partially updates data, leaving inconsistent embeddings.
- Old corpus remains active after new data is fetched.
- Refresh log does not record failures clearly.

### 6.3 Change Detection
- Minor data shifts trigger false anomaly alerts.
- Significant scheme changes are missed by detection rules.
- Scheduler refreshes during source maintenance windows.

## 7. UI Integration

### 7.1 User Input
- User enters misspelled scheme names or non-standard abbreviations.
- User submits empty or very short queries.
- User enters multiple separate questions in one request.

### 7.2 Display and Formatting
- UI truncates source citation or footer text.
- Response rendering breaks for long lines or HTML characters.
- Advisory refusal appears as an error instead of a valid response.

### 7.3 API and Backend
- Backend `/query` endpoint returns 500 errors on malformed requests.
- UI fails to render when API latency is high.
- Incorrect response payload structure causes frontend failure.

## 8. Testing & Evaluation

### 8.1 Test Coverage Gaps
- Edge cases not covered by unit tests, e.g. malformed HTML or missing fields.
- No regression test for advisory detection logic.
- Response formatting not validated for sentence count.

### 8.2 Data Validation
- Sample queries do not include all critical data points such as account statement process or capital gains certificate.
- Tests assume exact data formatting and fail on legitimate source variation.

### 8.3 Quality Evaluation
- Manual evaluation misses subtle citation mismatches.
- Response quality is judged only on retrieval and not on compliance style.

## 9. Deployment and Local Run

### 9.1 Local Environment
- Required dependencies fail to install due to missing system packages.
- Scheduler requires a separate process and is not started automatically.
- Environment variables for embedding keys or vector store are missing.

### 9.2 Reproducibility
- README instructions are incomplete or outdated.
- Local deployment fails without explicit startup sequence for ingestion and UI.

## 10. Additional Corner Cases

### 10.1 Multi-Scheme Queries
- Queries ask about more than one scheme at once, e.g. “What is the exit load for HDFC Mid Cap and Large Cap?”
- The orchestrator must either answer the first scheme only or ask for clarification.

### 10.2 Performance-Related Questions
- Queries ask for returns, best-performing schemes, or comparisons.
- The system must refuse and provide a regulatory link.

### 10.3 Out-of-Scope Schemes
- Queries mention a fund outside the 10 HDFC schemes.
- The system should respond that the corpus does not cover that scheme and link to official sources.

### 10.4 Unexpected User Behavior
- User attempts SQL injection or malicious query text.
- User asks for system internals or training data.
- User inputs multi-language text or non-English terms.

### 10.5 Source Updates During Query
- A source changes while a query is being processed.
- The system should maintain consistency by using the corpus snapshot active at query time.

## Notes
- This edge-case document assumes a single-developer implementation and aims to cover practical failure modes across ingestion, retrieval, classification, scheduler, UI, and deployment.
- Prioritize handling the most likely failures first: missing fields, advisory query detection, citation validity, and scheduler refresh consistency.

# Project Context

## Project Name
Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Objective
Build a lightweight Retrieval-Augmented Generation (RAG) assistant that answers factual mutual fund queries using official public sources only.

## Scope
- Select one Asset Management Company (AMC): **HDFC Funds**
- Collect 15–25 official public URLs from sources such as AMC factsheets, KIM, SID, AMC FAQ/help pages, AMFI, SEBI guidance pages, and statement/tax document download guides
- Use the curated corpus to answer factual questions about mutual fund schemes
- Provide concise, source-backed responses only

## Curated Corpus of Sources

### Groww - HDFC Funds (10 Schemes)
1. https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth
2. https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth
3. https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth
4. https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth
5. https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth
6. https://groww.in/mutual-funds/hdfc-balanced-advantage-fund-direct-growth
7. https://groww.in/mutual-funds/hdfc-nifty-50-index-fund-direct-growth
8. https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth
9. https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth
10. https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth

### HDFC Official Sources (4 Documents)
1. https://www.hdfcfund.com/investor-services/fund-documents/kim
2. https://www.hdfcfund.com/investor-services/fund-documents/sid
3. https://www.hdfcfund.com/information/online-services-investors
4. https://www.hdfcfund.com/services/consolidated-account-statement

### AMFI & SEBI (2 Resources)
1. https://www.amfiindia.com/investor
2. https://investor.sebi.gov.in/understanding_mf.html

## Fund Management Data - Chatbot Response Data

The chatbot should retrieve and respond with the following fund management data:
- **Scheme Name & Type** (e.g., HDFC Mid Cap Fund - Equity)
- **Expense Ratio** (percentage)
- **Minimum Investment** (lump sum and SIP amounts)
- **Exit Load** (percentage and lock-in period)
- **Riskometer Classification** (Low, Low-Moderate, Moderate, Moderate-High, High)
- **Benchmark Index** (e.g., Nifty 500, BSE Sensex)
- **Fund Manager Information** (name and experience)
- **Asset Under Management (AUM)** (in Rs. Crores)
- **Category & Sub-category** (e.g., Equity > Large Cap, Debt, Hybrid)
- **Key Information Memorandum (KIM)** link
- **Scheme Information Document (SID)** link
- **Account Statement Download** process
- **Tax Document** (Capital Gains Certificate) availability

## Chatbot Response Requirements
- Answer objective factual queries using the fund management data above
- Limit each response to a maximum of 3 sentences
- Include exactly one citation link per response (sourced from the curated corpus)
- Include footer: `Last updated from sources: <date>`
- Quote accurate data directly from official sources (Groww, HDFC, AMFI, SEBI)

## Refusal Handling
- Refuse non-factual or advisory questions
- Examples of advisory queries to refuse:
  - "Should I invest in this fund?"
  - "Which fund is better?"
- Refusal responses must be polite, clear, facts-only, and include a relevant educational link (e.g., AMFI or SEBI)

## User Interface Requirements
- Simple interface with:
  - a welcome message
  - three example questions
  - a visible disclaimer: "Facts-only. No investment advice."

## Constraints
- Use only official public sources (AMC, AMFI, SEBI)
- Do not use third-party blogs or aggregator websites
- Do not collect or process personal data such as PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers
- No investment advice, recommendations, performance comparisons, or return calculations
- For performance-related queries, provide an official factsheet link only
- Responses must be short, factual, and verifiable
- Every answer must include a source link and last updated date

## Expected Deliverables
- README document with setup instructions, selected AMC/schemes, architecture overview, known limitations, and disclaimer snippet
- Minimal user interface meeting the design requirements

## Success Criteria
- Accurate retrieval of factual mutual fund information
- Strict facts-only responses
- Consistent valid source citations
- Proper refusal of advisory queries
- Clean, minimal, user-friendly interface

## Disclaimer
Facts-only. No investment advice.

## Final Architecture Decision

- Embedding Model (primary): BAAI/bge-small-en-v1.5
- Vector Store (primary): ChromaDB (local persistent database)

Notes: Other vector stores (FAISS, Pinecone, Milvus, Weaviate) and embedding models may be mentioned elsewhere as future scalability options but are no longer the primary choices for this repository.

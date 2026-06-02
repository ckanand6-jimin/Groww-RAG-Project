import datetime
import re
from enum import Enum
from typing import List, Tuple


class QueryType(str, Enum):
    FACTUAL = "FACTUAL"
    ADVISORY = "ADVISORY"
    AMBIGUOUS = "AMBIGUOUS"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


EDUCATION_LINK = "https://www.amfiindia.com/investor"
LAST_UPDATED = datetime.date.today().isoformat()

ADVISORY_PATTERNS: List[str] = [
    "should i",
    "should you",
    "should we",
    "recommend",
    "advice",
    "advise",
    "investment advice",
    "invest in",
    "buy",
    "sell",
    "best fund",
    "best scheme",
    "which is better",
    "where should",
    "help me choose",
    "what should i",
    "how much should i",
    "can i invest",
    "is it worth",
    "would it be",
    "would i",
    "could i",
    "which fund",
    "which scheme",
    "what to invest",
    "investment decision",
    "portfolio",
    "compare returns",
    "compare performance",
    "forecast",
    "predict",
    "performance",
    "returns",
    "profit",
    "recommendation",
    "financial advisor",
    "advisor",
    "suitable for",
]

AMBIGUOUS_PATTERNS: List[str] = [
    "what do you think",
    "not sure",
    "any advice",
    "is this good",
    "does it make sense",
    "could be",
    "maybe",
    "should i consider",
    "am i right",
]

OUT_OF_SCOPE_PATTERNS: List[str] = [
    "crypto",
    "bitcoin",
    "nft",
    "forex",
    "real estate",
    "insurance",
    "loan",
    "mortgage",
    "tax planning",
]


def normalize_query(query: str) -> str:
    text = query.strip().lower()
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _contains_any(text: str, patterns: List[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def classify_query(query: str) -> Tuple[QueryType, List[str]]:
    normalized = normalize_query(query)
    if not normalized:
        return QueryType.OUT_OF_SCOPE, []

    matches: List[str] = []
    if _contains_any(normalized, OUT_OF_SCOPE_PATTERNS):
        return QueryType.OUT_OF_SCOPE, [p for p in OUT_OF_SCOPE_PATTERNS if p in normalized]

    advisory_matches = [pattern for pattern in ADVISORY_PATTERNS if pattern in normalized]
    if advisory_matches:
        return QueryType.ADVISORY, advisory_matches

    ambiguous_matches = [pattern for pattern in AMBIGUOUS_PATTERNS if pattern in normalized]
    if ambiguous_matches:
        return QueryType.AMBIGUOUS, ambiguous_matches

    if normalized.endswith("?") and len(normalized.split()) < 3:
        return QueryType.AMBIGUOUS, [normalized]

    return QueryType.FACTUAL, []


def build_refusal_response(query: str, query_type: QueryType) -> dict:
    if query_type == QueryType.ADVISORY:
        body = (
            "I can only provide factual information about mutual fund schemes. "
            "I cannot recommend specific funds, give investment advice, or make portfolio decisions. "
            f"Please consult a qualified financial advisor for personalized guidance. "
            f"For investor education, see {EDUCATION_LINK}."
        )
    elif query_type == QueryType.AMBIGUOUS:
        body = (
            "Your question appears to ask for advice or a recommendation rather than a factual mutual fund fact. "
            "I can only answer factual queries about HDFC mutual fund scheme details. "
            f"For investor guidance, see {EDUCATION_LINK}."
        )
    else:
        body = (
            "I could not classify your question as a factual mutual fund query. "
            "I can only answer factual questions about HDFC mutual fund schemes. "
            f"For investor education, see {EDUCATION_LINK}."
        )

    return {
        "query": query,
        "response_type": "REFUSAL",
        "query_type": query_type.value,
        "answer": body,
        "citation": EDUCATION_LINK,
        "source_url": EDUCATION_LINK,
        "last_updated": LAST_UPDATED,
        "provider": "refusal",
        "hits": [],
    }

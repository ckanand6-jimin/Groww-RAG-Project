import os
import re
from typing import Any, Dict, List, Optional, Sequence

import torch
from transformers import AutoModel, AutoTokenizer

from .corpus import ROOT, SCHEME_METADATA
from .embed import mean_pooling
from .vector_db import ensure_collection, init_chroma

CHROMA_DIR = ROOT / "data" / "chroma_db"
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "mutual_fund_chunks")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
MAX_RESULTS = int(os.environ.get("RETRIEVE_TOP_K", "5"))

SECTION_KEYWORDS: Dict[str, List[str]] = {
    "expense_ratio": ["expense ratio", "expense", "expense ratio direct"],
    "exit_load": ["exit load", "exit-load", "exitload"],
    "minimum_investment": ["minimum investment", "sip", "sip amount", "lump sum", "minimum lump sum"],
    "benchmark": ["benchmark", "index"],
    "riskometer": ["riskometer", "risk rating", "risk"],
    "fund_management": ["fund manager", "fund management", "fund manager name"],
    "aum": ["aum", "assets under management", "asset under management"],
    "investment_objective": ["investment objective", "objective", "purpose"],
    "fund_house": ["fund house", "amc", "asset management company", "asset manager"],
    "documents": ["kim", "sid", "scheme information document", "key information memorandum"],
    "overview": ["overview", "summary", "about"],
}

OFFICIAL_DOMAINS = ["hdfcfund.com", "amfiindia.com", "sebi.gov.in"]


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def load_embedding_model(model_name: str = EMBEDDING_MODEL):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).to(device)
    model.eval()
    return tokenizer, model, device


def embed_query(query: str, tokenizer: AutoTokenizer, model: AutoModel, device: torch.device) -> List[float]:
    if not query or not query.strip():
        raise ValueError("Query text must not be empty.")
    encoded = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
    input_ids = encoded["input_ids"].to(device)
    attention_mask = encoded["attention_mask"].to(device)
    with torch.no_grad():
        output = model(input_ids=input_ids, attention_mask=attention_mask)
    pooled = mean_pooling(output, attention_mask)
    return pooled.cpu().numpy().tolist()[0]


def build_scheme_alias_map() -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for scheme_id, metadata in SCHEME_METADATA.items():
        scheme_name = metadata.get("scheme_name") or ""
        normalized_name = normalize_text(scheme_name)
        if normalized_name:
            alias_map[scheme_id] = normalized_name
    return alias_map


def detect_scheme_filter(query: str, alias_map: Dict[str, str]) -> Optional[str]:
    normalized_query = normalize_text(query)
    for scheme_id, alias in alias_map.items():
        if alias in normalized_query:
            return scheme_id
        if scheme_id.replace("_", " ") in normalized_query:
            return scheme_id
    return None


def detect_section_filter(query: str) -> Optional[str]:
    normalized_query = normalize_text(query)
    for section, patterns in SECTION_KEYWORDS.items():
        for pattern in patterns:
            if pattern in normalized_query:
                return section
    return None


def build_metadata_filter(scheme_id: Optional[str] = None, section: Optional[str] = None) -> Dict[str, Any]:
    if scheme_id and section:
        return {"$and": [{"scheme_id": scheme_id}, {"section": section}]}
    if scheme_id:
        return {"scheme_id": scheme_id}
    if section:
        return {"section": section}
    return {}


def compute_similarity(distance: float) -> float:
    return 1.0 / (1.0 + distance)


def compute_bonus(metadata: Dict[str, Any], query: str, scheme_filter: Optional[str], section_filter: Optional[str]) -> float:
    bonus = 0.0
    url = (metadata.get("source_url") or "").lower()
    if any(domain in url for domain in OFFICIAL_DOMAINS):
        bonus += 0.12

    if scheme_filter and metadata.get("scheme_id") == scheme_filter:
        bonus += 0.16

    scheme_meta = SCHEME_METADATA.get(metadata.get("scheme_id")) or {}
    scheme_name = normalize_text(str(scheme_meta.get("scheme_name", "")))
    if scheme_name and scheme_name in normalize_text(query):
        bonus += 0.08

    if section_filter and metadata.get("section") == section_filter:
        bonus += 0.08

    return bonus


def _flatten_result_list(value: Sequence[Any]) -> Sequence[Any]:
    if len(value) == 1 and isinstance(value[0], list):
        return value[0]
    return value


def rerank_results(results: Dict[str, Sequence[Any]], query: str, scheme_filter: Optional[str], section_filter: Optional[str]) -> List[Dict[str, Any]]:
    reranked: List[Dict[str, Any]] = []
    query_lower = normalize_text(query)
    documents = _flatten_result_list(results.get("documents", []))
    metadatas = _flatten_result_list(results.get("metadatas", []))
    distances = _flatten_result_list(results.get("distances", []))

    for index, metadata in enumerate(metadatas):
        document = documents[index] if index < len(documents) else ""
        distance = distances[index] if index < len(distances) else 1.0
        similarity = compute_similarity(distance)
        bonus = compute_bonus(metadata or {}, query_lower, scheme_filter, section_filter)
        score = similarity + bonus
        reranked.append(
            {
                "document": document,
                "metadata": metadata,
                "distance": distance,
                "score": round(score, 4),
                "similarity": round(similarity, 4),
                "authority_bonus": round(bonus, 4),
            }
        )

    return sorted(reranked, key=lambda item: item["score"], reverse=True)


def extract_scheme_candidates(hits: List[Dict[str, Any]], max_candidates: int = 4) -> List[str]:
    seen = []
    for hit in hits:
        scheme_id = hit.get("metadata", {}).get("scheme_id")
        if not scheme_id or scheme_id in seen:
            continue
        seen.append(scheme_id)
        if len(seen) >= max_candidates:
            break
    return [SCHEME_METADATA.get(s, {}).get("scheme_name", s) or s for s in seen]


def retrieve(query: str, top_k: int = MAX_RESULTS) -> Dict[str, Any]:
    tokenizer, model, device = load_embedding_model()
    query_embedding = embed_query(query, tokenizer, model, device)
    scheme_alias_map = build_scheme_alias_map()
    scheme_filter = detect_scheme_filter(query, scheme_alias_map)
    section_filter = detect_section_filter(query)
    client = init_chroma(persist_dir=CHROMA_DIR)
    collection = ensure_collection(client, COLLECTION_NAME)
    where_filter = build_metadata_filter(scheme_filter, section_filter)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter if where_filter else None,
        include=["documents", "metadatas", "distances"],
    )

    hits = rerank_results(results, query, scheme_filter, section_filter)
    scheme_candidates = []
    if not scheme_filter and hits:
        scheme_candidates = extract_scheme_candidates(hits)
    return {
        "query": query,
        "scheme_filter": scheme_filter,
        "section_filter": section_filter,
        "retrieval_count": len(hits),
        "hits": hits,
        "scheme_candidates": scheme_candidates,
    }


def format_search_output(results: Dict[str, Any]) -> str:
    lines: List[str] = [f"Query: {results['query']}"]
    if results["scheme_filter"]:
        lines.append(f"Scheme filter: {results['scheme_filter']}")
    if results["section_filter"]:
        lines.append(f"Section filter: {results['section_filter']}")
    lines.append("Top hits:")
    for hit in results["hits"]:
        lines.append(
            f"- {hit['metadata'].get('scheme_id')} | {hit['metadata'].get('section')} | score={hit['score']} | source={hit['metadata'].get('source_url')}"
        )
        lines.append(f"  text: {hit['document'][:220].strip()}...")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Retrieve relevant chunks from ChromaDB for a query.")
    parser.add_argument("query", type=str, help="User query text")
    parser.add_argument("--top-k", type=int, default=MAX_RESULTS, help="Number of candidate chunks to return")
    args = parser.parse_args()

    output = retrieve(args.query, top_k=args.top_k)
    print(format_search_output(output))


if __name__ == "__main__":
    main()

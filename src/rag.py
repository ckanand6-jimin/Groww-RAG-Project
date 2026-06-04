import datetime
import os
import re
from typing import Any, Dict, List, Optional

import requests

from .query_classifier import QueryType, build_refusal_response, classify_query
from .retrieve import retrieve

GROQ_MODEL = os.environ.get("GROQ_MODEL", "groq/llm-small")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_API_URL = os.environ.get("GROQ_API_URL", "https://api.groq.com/v1/responses")
MAX_CONTEXT_CHUNKS = int(os.environ.get("RAG_MAX_CHUNKS", "4"))
LAST_UPDATED = datetime.date.today().isoformat()


def _normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def _truncate_to_sentences(text: str, count: int = 2) -> str:
    normalized = _normalize_text(text)
    sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+(?=[A-Z])', normalized) if s.strip()]
    if not sentences:
        return normalized
    truncated = " ".join(sentences[:count])
    return truncated if truncated.endswith(('.', '?', '!')) else f"{truncated}."


def _hit_summary(hit: Dict[str, Any]) -> str:
    metadata = hit.get("metadata", {}) or {}
    document = _normalize_text(hit.get("document", ""))
    section = metadata.get("section_title") or metadata.get("section") or "section"
    scheme = metadata.get("scheme_id") or "unknown scheme"
    source = metadata.get("source_url") or "unknown source"
    if document:
        return f"{section} for {scheme}: {document} [source: {source}]"
    return f"{section} for {scheme} [source: {source}]"


def _build_context(hits: List[Dict[str, Any]]) -> str:
    return "\n\n".join(_hit_summary(hit) for hit in hits[:MAX_CONTEXT_CHUNKS])


def _build_prompt(query: str, hits: List[Dict[str, Any]]) -> str:
    instruction = (
        "You are a facts-only mutual fund assistant. Answer the user query using only the provided source excerpts. "
        "Do not hallucinate, do not provide investment advice, and do not introduce new information. "
        "Use exactly one citation in square brackets with the source URL. "
        "Keep the answer to 1-3 sentences. "
        "Append 'Last updated from sources: YYYY-MM-DD' at the end."
    )
    context = _build_context(hits)
    prompt = (
        f"{instruction}\n\n"
        f"User query: {query}\n\n"
        "Source excerpts:\n"
        f"{context}\n\n"
        "Answer:"
    )
    return prompt


def _parse_groq_response(response_json: Dict[str, Any]) -> Optional[str]:
    if not isinstance(response_json, dict):
        return None
    output = response_json.get("output")
    if isinstance(output, list) and output:
        first = output[0]
        if isinstance(first, dict):
            content = first.get("content")
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        text = item.get("text")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return _normalize_text(" ".join(parts))
            text = first.get("text")
            if isinstance(text, str):
                return _normalize_text(text)
    if isinstance(response_json.get("response"), str):
        return _normalize_text(response_json["response"])
    if isinstance(response_json.get("text"), str):
        return _normalize_text(response_json["text"])
    return None


def _call_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "input": prompt,
        "temperature": 0.0,
        "max_output_tokens": 512,
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    parsed = _parse_groq_response(response.json())
    if not parsed:
        raise ValueError("Unable to parse Groq response")
    return parsed


def _format_fallback_answer(query: str, hits: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not hits:
        return {
            "query": query,
            "answer": "I could not find a factual answer in the available HDFC corpus.",
            "citation": None,
            "source_url": None,
            "last_updated": LAST_UPDATED,
            "provider": "fallback",
            "hits": [],
        }

    top_hit = hits[0]
    text = _truncate_to_sentences(top_hit.get("document", ""), count=2)
    source_url = top_hit.get("metadata", {}).get("source_url")
    answer = text
    return {
        "query": query,
        "answer": answer,
        "citation": source_url,
        "source_url": source_url,
        "last_updated": LAST_UPDATED,
        "provider": "fallback",
        "hits": hits,
    }


def answer_query(query: str) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Query text must not be empty.")

    query_type, triggers = classify_query(query)
    if query_type != QueryType.FACTUAL:
        refusal = build_refusal_response(query, query_type)
        refusal["triggers"] = triggers
        return refusal

    retrieval = retrieve(query, top_k=MAX_CONTEXT_CHUNKS)
    hits = retrieval.get("hits", [])
    result: Dict[str, Any]

    if GROQ_API_KEY and hits:
        prompt = _build_prompt(query, hits)
        try:
            answer_text = _call_groq(prompt)
            source_url = hits[0].get("metadata", {}).get("source_url")
            result = {
                "query": query,
                "answer": answer_text,
                "citation": source_url,
                "source_url": source_url,
                "last_updated": LAST_UPDATED,
                "provider": "groq",
                "response_type": "FACTUAL",
                "hits": hits,
                "query_type": query_type.value,
            }
        except Exception as exc:
            fallback = _format_fallback_answer(query, hits)
            fallback["error"] = str(exc)
            fallback["query_type"] = query_type.value
            result = fallback
    else:
        result = _format_fallback_answer(query, hits)
        result["query_type"] = query_type.value
        result["response_type"] = "FACTUAL"

    result["retrieval"] = retrieval
    if retrieval.get("scheme_candidates"):
        result["scheme_matches"] = retrieval["scheme_candidates"]
        result["original_query"] = query
    return result


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Compose a RAG answer for a mutual fund query.")
    parser.add_argument("query", type=str, help="User query text")
    args = parser.parse_args()

    response = answer_query(args.query)
    print(response["answer"])


if __name__ == "__main__":
    main()

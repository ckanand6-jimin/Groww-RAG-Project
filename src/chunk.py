import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .corpus import ROOT

CORPUS_INPUT = ROOT / "data" / "corpus.json"
CHUNKS_OUTPUT = ROOT / "data" / "chunks.json"

SECTION_FIELD_MAP = {
    "overview": ["scheme_name"],
    "expense_ratio": ["expense_ratio"],
    "exit_load": ["exit_load"],
    "minimum_investment": ["minimum_sip", "minimum_lumpsum"],
    "benchmark": ["benchmark"],
    "riskometer": ["riskometer"],
    "fund_management": ["fund_manager"],
    "investment_objective": ["investment_objective"],
    "fund_house": ["amc_name"],
}

SECTION_TITLES = {
    "overview": "Overview",
    "expense_ratio": "Expense Ratio",
    "exit_load": "Exit Load",
    "minimum_investment": "Minimum Investment",
    "benchmark": "Benchmark",
    "riskometer": "Riskometer",
    "fund_management": "Fund Management",
    "investment_objective": "Investment Objective",
    "fund_house": "Fund House",
    "raw_summary": "Raw Summary",
}


def normalize_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    return " ".join(str(text).split()).strip()


def is_empty_text(text: Optional[str]) -> bool:
    normalized = normalize_text(text)
    return normalized.lower() in {"", "null", "none", "n/a"}


def build_chunk_id(scheme_id: str, section_name: str) -> str:
    return f"{scheme_id}__{section_name}"


def build_section_chunk(
    scheme_id: str,
    source_url: Optional[str],
    section_name: str,
    section_data: Dict[str, Any],
    structured_fields: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    text = normalize_text(section_data.get("text"))
    if is_empty_text(text):
        return None

    title = SECTION_TITLES.get(section_name, section_name.replace("_", " ").title())
    chunk_text = text if section_name == "overview" else f"{title}: {text}"

    structured_value = section_data.get("structured")
    if structured_value is None:
        field_names = SECTION_FIELD_MAP.get(section_name, [])
        if len(field_names) == 1:
            structured_value = structured_fields.get(field_names[0])
        else:
            fallback_dict: Dict[str, Any] = {}
            for field_name in field_names:
                if field_name in structured_fields:
                    fallback_dict[field_name] = structured_fields[field_name]
            structured_value = fallback_dict or None

    if isinstance(structured_value, dict) and not structured_value:
        structured_value = None

    return {
        "chunk_id": build_chunk_id(scheme_id, section_name),
        "scheme_id": scheme_id,
        "source_url": source_url,
        "section": section_name,
        "section_title": title,
        "text": chunk_text,
        "structured": structured_value,
        "field_names": SECTION_FIELD_MAP.get(section_name, []),
    }


def build_summary_chunk(
    scheme_id: str,
    source_url: Optional[str],
    text: Optional[str],
) -> Optional[Dict[str, Any]]:
    normalized = normalize_text(text)
    if is_empty_text(normalized):
        return None

    return {
        "chunk_id": build_chunk_id(scheme_id, "raw_summary"),
        "scheme_id": scheme_id,
        "source_url": source_url,
        "section": "raw_summary",
        "section_title": SECTION_TITLES["raw_summary"],
        "text": normalized,
        "structured": None,
        "field_names": [],
    }


def chunk_record(record: Dict[str, Any]) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    scheme_id = record.get("scheme_id")
    source_url = record.get("sources", {}).get("groww_url")
    structured_fields = record.get("structured_fields") or {}
    sections = record.get("sections") or {}

    if isinstance(sections, dict):
        for section_name, section_data in sections.items():
            if not isinstance(section_data, dict):
                continue
            chunk = build_section_chunk(scheme_id, source_url, section_name, section_data, structured_fields)
            if chunk is not None:
                chunks.append(chunk)

    summary_chunk = build_summary_chunk(scheme_id, source_url, record.get("scheme_text"))
    if summary_chunk is not None:
        chunks.append(summary_chunk)

    if not chunks and record.get("scheme_text"):
        fallback = build_summary_chunk(scheme_id, source_url, record.get("scheme_text"))
        if fallback is not None:
            chunks.append(fallback)

    return chunks


def load_corpus() -> List[Dict[str, Any]]:
    if not CORPUS_INPUT.exists():
        raise FileNotFoundError(f"Corpus file not found: {CORPUS_INPUT}")
    with CORPUS_INPUT.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_chunks(chunks: List[Dict[str, Any]]) -> None:
    CHUNKS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(chunks, handle, indent=2, ensure_ascii=False)


def chunk_corpus() -> List[Dict[str, Any]]:
    records = load_corpus()
    all_chunks: List[Dict[str, Any]] = []
    for record in records:
        all_chunks.extend(chunk_record(record))
    return all_chunks


def main() -> None:
    chunks = chunk_corpus()
    save_chunks(chunks)
    print(f"Saved {len(chunks)} chunks to {CHUNKS_OUTPUT}")


if __name__ == "__main__":
    main()

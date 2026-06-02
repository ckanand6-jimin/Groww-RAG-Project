import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .corpus import ALL_SOURCE_URLS, GROWW_HDFC_FUNDS, HDFC_OFFICIAL_SOURCES, SCHEME_METADATA, ROOT
from .schema import AccountServices, DocumentLinks, FundScheme, SourceInfo

DATA_PATH = ROOT / "data"
DATA_PATH.mkdir(exist_ok=True)
RAW_PATH = DATA_PATH / "raw"
RAW_PATH.mkdir(exist_ok=True)
JSON_OUTPUT = DATA_PATH / "corpus.json"
RAW_INDEX_OUTPUT = DATA_PATH / "raw_index.json"
SQLITE_OUTPUT = DATA_PATH / "corpus.db"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

SESSION = requests.Session()
RETRY_STRATEGY = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    backoff_factor=1,
)
SESSION.mount("https://", HTTPAdapter(max_retries=RETRY_STRATEGY))
SESSION.mount("http://", HTTPAdapter(max_retries=RETRY_STRATEGY))

FIELD_PATTERNS = {
    "expense_ratio": [r"expense ratio", r"expense ratio \(direct\)", r"expense ratio\s*[:\-–]"],
    "minimum_investment_lump_sum": [r"minimum investment.*lump sum", r"minimum lump sum", r"minimum investment"],
    "minimum_investment_sip": [r"minimum sip", r"sip amount", r"minimum investment.*sip"],
    "exit_load": [r"exit load", r"exit load.*%"],
    "lock_in_period": [r"lock[- ]?in period", r"lock[- ]?in"],
    "riskometer_class": [r"riskometer", r"risk rating"],
    "benchmark_index": [r"benchmark", r"benchmark index"],
    "fund_manager_name": [r"fund manager", r"fund managers"],
    "current_aum": [r"aum", r"asset under management", r"aum\s*:\s*"],
    "inception_date": [r"inception date", r"launched on", r"inception"],
}


def fetch_url(url: str) -> Optional[str]:
    try:
        response = SESSION.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def find_field_from_text(text: str, patterns: List[str]) -> Optional[str]:
    for pattern in patterns:
        regex = re.compile(rf"{pattern}[:\s\-–]*([^\n\r]+)", re.I)
        match = regex.search(text)
        if match:
            return normalize_text(match.group(1))
    return None


def safe_filename_for_url(url: str) -> str:
    sanitized = re.sub(r"https?://", "", url)
    sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", sanitized)
    return sanitized[:200]


def save_raw_html(url: str, html: str) -> Path:
    filename = safe_filename_for_url(url) + ".html"
    output_path = RAW_PATH / filename
    output_path.write_text(html, encoding="utf-8")
    return output_path


def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    return normalize_text(text)


def scrape_groww_scheme(html: str) -> Dict[str, Optional[str]]:
    # Primary: extract __NEXT_DATA__ JSON if available
    soup = BeautifulSoup(html, "html.parser")
    text = clean_html(html)
    parsed: Dict[str, Optional[str]] = {"cleaned_text": text}

    # try to find Next.js data in script#_next_data or __NEXT_DATA__
    next_data = None
    next_script = soup.find("script", id="__NEXT_DATA__")
    if next_script and next_script.string:
        try:
            next_data = json.loads(next_script.string)
        except Exception:
            next_data = None

    if not next_data:
        # fallback: search scripts for 'mfServerSideData'
        for script in soup.find_all("script"):
            if not script.string:
                continue
            if "mfServerSideData" in script.string:
                # attempt to extract a JSON object
                try:
                    m = re.search(r"(\{.*\"mfServerSideData\".*\})", script.string, re.S)
                    if m:
                        next_data = json.loads(m.group(1))
                        break
                except Exception:
                    continue

    # title extraction
    title = None
    title_tag = soup.find(["h1", "h2", "h3"])
    if title_tag:
        title = normalize_text(title_tag.get_text())
    parsed["title"] = title

    if next_data:
        # navigate to props.pageProps.mfServerSideData where present
        props = next_data.get("props") if isinstance(next_data, dict) else None
        pageProps = props.get("pageProps") if isinstance(props, dict) else None
        mf = None
        if isinstance(pageProps, dict):
            mf = pageProps.get("mfServerSideData") or pageProps.get("mfServerSideDataText")

        # parse mfServerSideData if we found it
        structured: Dict[str, Optional[object]] = {}
        sections: Dict[str, Dict[str, Optional[object]]] = {}

        def walk_find(d, key_substring):
            if not isinstance(d, dict):
                return None
            for k, v in d.items():
                if key_substring in k.lower():
                    return v
                if isinstance(v, dict):
                    found = walk_find(v, key_substring)
                    if found is not None:
                        return found
            return None

        if mf and isinstance(mf, dict):
            # discover available fields
            discovered_keys = list(mf.keys())
            parsed["mf_keys"] = discovered_keys

            def find_first(*candidates):
                for cand in candidates:
                    v = walk_find(mf, cand)
                    if v is not None:
                        return v
                return None

            # map fields
            structured["scheme_name"] = find_first("schemename", "scheme_name", "name")
            structured["amc_name"] = find_first("amc", "amcname", "fundhouse")
            structured["scheme_type"] = find_first("schemetype", "type")
            structured["category"] = find_first("category", "fundcategory")
            structured["sub_category"] = find_first("subcategory", "sub_category")
            structured["expense_ratio"] = find_first("expenseratio", "expense_ratio")
            structured["benchmark"] = find_first("benchmark")
            structured["riskometer"] = find_first("riskometer", "risk")
            structured["nav"] = find_first("nav", "navvalue")
            structured["aum"] = find_first("aum", "assetundermanagement", "aums")
            structured["minimum_sip"] = find_first("minimumsip", "minsip", "minimum_sip")
            structured["minimum_lumpsum"] = find_first("minimumlumpsum", "minlumpsum", "minimum_lumpsum")
            structured["exit_load"] = find_first("exitload", "exit_load")
            structured["fund_manager"] = find_first("fundmanager", "fund_manager", "fundManagers")
            structured["investment_objective"] = find_first("objective", "investmentobjective", "fundobjective")

            # build sections
            def section_from_keys(name, keys, fallback_text=None):
                val = find_first(*keys)
                txt = None
                if val is None and fallback_text:
                    txt = fallback_text
                elif isinstance(val, (str, int, float)):
                    txt = str(val)
                else:
                    try:
                        txt = json.dumps(val, ensure_ascii=False)
                    except Exception:
                        txt = str(val)
                struct = None
                if isinstance(val, str):
                    # try parse percentage numbers
                    m = re.search(r"([0-9]+\.?[0-9]*)\s*%", val)
                    if m:
                        try:
                            struct = float(m.group(1))
                        except Exception:
                            struct = None
                elif isinstance(val, (int, float)):
                    struct = val
                return {"text": txt, "structured": struct}

            sections["overview"] = {"text": parsed.get("title") or None, "structured": {"scheme_name": structured.get("scheme_name")}}
            sections["expense_ratio"] = section_from_keys("expense_ratio", ("expenseratio", "expense_ratio"), fallback_text=None)
            sections["exit_load"] = section_from_keys("exit_load", ("exitload",))
            sections["minimum_investment"] = section_from_keys("minimum_investment", ("minimumsip", "minimumsip", "minimum_lumpsum", "minlumpsum"))
            sections["benchmark"] = section_from_keys("benchmark", ("benchmark",))
            sections["riskometer"] = section_from_keys("riskometer", ("riskometer",))
            sections["fund_management"] = section_from_keys("fund_management", ("fundmanager", "fund_managers", "fundManagers"))
            sections["investment_objective"] = section_from_keys("investment_objective", ("objective", "investmentobjective", "fundobjective"))
            sections["fund_house"] = section_from_keys("fund_house", ("amc", "amcname", "fundhouse"))

            parsed["structured_fields"] = structured
            parsed["sections"] = sections
            return parsed

    # Fallback: HTML-based parsing
    for key, patterns in FIELD_PATTERNS.items():
        parsed[key] = find_field_from_text(text, patterns)

    # Fallback for current AUM if the raw text has AUM labels
    if not parsed.get("current_aum"):
        aum_match = re.search(r"AUM[:\s]*([\d,\.]+\s*(Cr|Crore|Crores|₹)?)", text, re.I)
        if aum_match:
            parsed["current_aum"] = normalize_text(aum_match.group(1))

    return parsed


def parse_document_page(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find(["title", "h1", "h2"])
    page_title = normalize_text(title_tag.get_text()) if title_tag else None
    body_text = clean_html(html)
    summary = normalize_text(body_text[:1200])
    return {"page_title": page_title, "summary": summary, "cleaned_text": body_text}


def build_scheme_record(scheme_id: str, groww_data: Dict[str, Optional[str]]) -> FundScheme:
    metadata = SCHEME_METADATA.get(scheme_id, {})
    documents = DocumentLinks(
        kim_link=HDFC_OFFICIAL_SOURCES["kim"],
        sid_link=HDFC_OFFICIAL_SOURCES["sid"],
        factsheet_link=GROWW_HDFC_FUNDS[scheme_id],
        prospectus_link=None,
    )
    account_services = AccountServices(
        statement_download_link=HDFC_OFFICIAL_SOURCES["consolidated_account_statement"],
        statement_frequency=None,
        capital_gains_cert_availability=None,
        account_statement_process=None,
        online_services_link=HDFC_OFFICIAL_SOURCES["online_services"],
    )
    sources = SourceInfo(
        groww_url=GROWW_HDFC_FUNDS[scheme_id],
        hdfc_official_url=HDFC_OFFICIAL_SOURCES["online_services"],
        last_updated=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        data_version=1,
    )

    # If sections exist (from NEXT_DATA), build a concise human-readable summary
    summary_text = None
    if groww_data.get("sections"):
        secs = groww_data.get("sections")
        pieces = []
        if secs.get("overview") and secs["overview"].get("text"):
            pieces.append(secs["overview"]["text"])
        if secs.get("expense_ratio") and secs["expense_ratio"].get("text"):
            pieces.append(f"Expense Ratio: {secs['expense_ratio']['text']}")
        if secs.get("benchmark") and secs["benchmark"].get("text"):
            pieces.append(f"Benchmark: {secs['benchmark']['text']}")
        summary_text = " | ".join([p for p in pieces if p])

    return FundScheme(
        scheme_id=scheme_id,
        scheme_name=metadata.get("scheme_name", groww_data.get("title") or ""),
        scheme_type=metadata.get("scheme_type"),
        category=metadata.get("category"),
        expense_ratio=groww_data.get("expense_ratio"),
        minimum_investment_lump_sum=groww_data.get("minimum_investment_lump_sum"),
        minimum_investment_sip=groww_data.get("minimum_investment_sip"),
        exit_load=groww_data.get("exit_load"),
        exit_load_applicability=None,
        lock_in_period=groww_data.get("lock_in_period"),
        riskometer_class=groww_data.get("riskometer_class"),
        benchmark_index=groww_data.get("benchmark_index"),
        fund_manager_name=groww_data.get("fund_manager_name"),
        fund_manager_experience_years=None,
        current_aum=groww_data.get("current_aum"),
        inception_date=groww_data.get("inception_date"),
            scheme_text=summary_text or groww_data.get("cleaned_text"),
        sections=groww_data.get("sections"),
        structured_fields=groww_data.get("structured_fields"),
        documents=documents,
        account_services=account_services,
        sources=sources,
    )


def save_json(records: List[FundScheme]) -> None:
    with JSON_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(
            [record.model_dump(mode="json") for record in records],
            handle,
            indent=2,
            ensure_ascii=False,
        )


def save_sqlite(records: List[FundScheme]) -> None:
    conn = sqlite3.connect(SQLITE_OUTPUT)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schemes (
            scheme_id TEXT PRIMARY KEY,
            scheme_name TEXT,
            scheme_type TEXT,
            category TEXT,
            expense_ratio TEXT,
            minimum_investment_lump_sum TEXT,
            minimum_investment_sip TEXT,
            exit_load TEXT,
            lock_in_period TEXT,
            riskometer_class TEXT,
            benchmark_index TEXT,
            fund_manager_name TEXT,
            current_aum TEXT,
            inception_date TEXT,
            groww_url TEXT,
            hdfc_official_url TEXT,
            last_updated TEXT,
            data_version INTEGER
        )
        """
    )
    cur.execute(
        "DELETE FROM schemes"
    )
    for record in records:
        cur.execute(
            """
            INSERT INTO schemes (
                scheme_id, scheme_name, scheme_type, category, expense_ratio,
                minimum_investment_lump_sum, minimum_investment_sip, exit_load,
                lock_in_period, riskometer_class, benchmark_index,
                fund_manager_name, current_aum, inception_date,
                groww_url, hdfc_official_url, last_updated, data_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.scheme_id,
                record.scheme_name,
                record.scheme_type,
                record.category,
                record.expense_ratio,
                record.minimum_investment_lump_sum,
                record.minimum_investment_sip,
                record.exit_load,
                record.lock_in_period,
                record.riskometer_class,
                record.benchmark_index,
                record.fund_manager_name,
                record.current_aum,
                record.inception_date,
                str(record.sources.groww_url) if record.sources else None,
                str(record.sources.hdfc_official_url) if record.sources else None,
                record.sources.last_updated if record.sources else None,
                record.sources.data_version if record.sources else None,
            ),
        )
    conn.commit()
    conn.close()


def save_raw_index(records: List[Dict[str, Optional[str]]]) -> None:
    with RAW_INDEX_OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(records, handle, indent=2, ensure_ascii=False)


def fetch_all_corpus_sources() -> Dict[str, str]:
    raw_index: List[Dict[str, Optional[str]]] = []
    cache: Dict[str, str] = {}
    for url in ALL_SOURCE_URLS:
        html = fetch_url(url)
        page_type = "scheme_page" if url in GROWW_HDFC_FUNDS.values() else "official_document"
        raw_filename = None
        title = None
        cleaned_text = None
        fetched = False

        if html:
            raw_path = save_raw_html(url, html)
            raw_filename = str(raw_path.name)
            cleaned_text = clean_html(html)
            source_info = parse_document_page(html)
            title = source_info.get("page_title")
            cache[url] = html
            fetched = True

        raw_index.append(
            {
                "url": url,
                "page_type": page_type,
                "raw_filename": raw_filename,
                "fetched": fetched,
                "title": title,
                "cleaned_text_snippet": cleaned_text[:800] if cleaned_text else None,
            }
        )
    save_raw_index(raw_index)
    return cache


def ingest_corpus() -> List[FundScheme]:
    source_cache = fetch_all_corpus_sources()
    records: List[FundScheme] = []
    for scheme_id, url in GROWW_HDFC_FUNDS.items():
        html = source_cache.get(url)
        groww_data: Dict[str, Optional[str]] = {}
        if html:
            groww_data = scrape_groww_scheme(html)
        record = build_scheme_record(scheme_id, groww_data)
        records.append(record)
    return records


def main() -> None:
    records = ingest_corpus()
    save_json(records)
    save_sqlite(records)
    print(f"Saved {len(records)} scheme records to {JSON_OUTPUT} and {SQLITE_OUTPUT}")
    print(f"Saved raw HTML files to {RAW_PATH}")
    print(f"Saved raw index details to {RAW_INDEX_OUTPUT}")


if __name__ == "__main__":
    main()

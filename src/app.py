import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .rag import answer_query
from .vector_db import init_chroma, ensure_collection

app = FastAPI()

@app.get("/debug-chroma")
def debug_chroma():
    client = init_chroma()
    collection = ensure_collection(client)

    return {
        "collection": collection.name,
        "count": collection.count()
    }

@app.get("/debug-sample")
def debug_sample():
    client = init_chroma()
    collection = ensure_collection(client)

    result = collection.get(limit=5)

    return result

@app.get("/debug-query")
def debug_query():
    client = init_chroma()
    collection = ensure_collection(client)

    results = collection.get(
        where={"scheme_id": "hdfc_large_cap_fund_direct_growth"}
    )

    return {
        "count": len(results.get("ids", [])),
        "results": results
    }
@app.get("/debug-search")
def debug_search():
    from .retrieve import retrieve

    return retrieve("HDFC Large Cap Fund")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
LOG_FILE = Path(__file__).resolve().parent.parent / "data" / "logs" / "refresh.log"

if os.environ.get("ENABLE_SCHEDULER", "0") == "1":
    from .scheduler import start_scheduler

    start_scheduler()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/app.css")
def app_css():
    return FileResponse(STATIC_DIR / "app.css")

@app.get("/app.js")
def app_js():
    return FileResponse(STATIC_DIR / "app.js")

@app.get("/refresh-status")
def refresh_status():
    if not LOG_FILE.exists():
        return {
            "available": False,
            "last_refresh": None,
            "recent_entries": [],
        }
    try:
        raw = LOG_FILE.read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        recent_entries = lines[-10:]
        last_refresh = None
        for line in reversed(recent_entries):
            if "REFRESH_COMPLETION" in line:
                last_refresh = line.strip()
                break
        return {
            "available": True,
            "last_refresh": last_refresh or (recent_entries[-1] if recent_entries else None),
            "recent_entries": recent_entries,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/query")
def query_faq(request: QueryRequest):
    return answer_query(request.query)

@app.get("/query")
def query_faq_get(q: str):
    return answer_query(q)

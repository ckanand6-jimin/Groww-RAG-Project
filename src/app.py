import os
from fastapi import FastAPI
from pydantic import BaseModel

from .rag import answer_query

app = FastAPI()

if os.environ.get("ENABLE_SCHEDULER", "0") == "1":
    from .scheduler import start_scheduler

    start_scheduler()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"message": "Mutual Fund FAQ Assistant backend is running."}

@app.post("/query")
def query_faq(request: QueryRequest):
    return answer_query(request.query)

@app.get("/query")
def query_faq_get(q: str):
    return answer_query(q)

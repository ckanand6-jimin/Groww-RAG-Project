import os
import json
from pathlib import Path
from typing import List

import torch
from transformers import AutoTokenizer, AutoModel
import chromadb
from chromadb.config import Settings

from .corpus import ROOT

CHUNKS_INPUT = ROOT / "data" / "chunks.json"
CHROMA_DIR = ROOT / "data" / "chroma_db"
METADATA_OUTPUT = ROOT / "data" / "embeddings_meta.json"

# Config via env
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
BATCH_SIZE = int(os.environ.get("EMBED_BATCH", "8"))


def load_chunks() -> List[dict]:
    if not CHUNKS_INPUT.exists():
        raise FileNotFoundError(f"Chunks file not found: {CHUNKS_INPUT}")
    with CHUNKS_INPUT.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_text_payload(chunk: dict) -> str:
    parts = [chunk.get("text", "")]
    structured = chunk.get("structured")
    if structured:
        try:
            if isinstance(structured, (dict, list)):
                parts.append(json.dumps(structured, ensure_ascii=False))
            else:
                parts.append(str(structured))
        except Exception:
            parts.append(str(structured))
    return " \n ".join([p for p in parts if p])


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask


def embed_texts(model, tokenizer, texts: List[str], device: torch.device) -> List[List[float]]:
    embeddings = []
    model.to(device)
    model.eval()
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        enc = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        input_ids = enc["input_ids"].to(device)
        attention_mask = enc["attention_mask"].to(device)
        with torch.no_grad():
            out = model(input_ids=input_ids, attention_mask=attention_mask)
        emb = mean_pooling(out, attention_mask)
        emb = emb.cpu().numpy()
        embeddings.extend(emb.tolist())
    return embeddings


def main():
    print(f"Embedding model: {EMBEDDING_MODEL}")
    chunks = load_chunks()
    texts = [build_text_payload(c) for c in chunks]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    model = AutoModel.from_pretrained(EMBEDDING_MODEL)

    print("Computing embeddings...")
    embeddings = embed_texts(model, tokenizer, texts, device)

    # Initialize ChromaDB client with local persistence
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.Client(Settings(persist_directory=str(CHROMA_DIR), is_persistent=True))
    collection = client.get_or_create_collection(name="mutual_fund_chunks")

    ids = [c.get("chunk_id") for c in chunks]
    documents = [c.get("text") for c in chunks]
    metadatas = []
    for c in chunks:
        md = {
            "chunk_id": c.get("chunk_id"),
            "scheme_id": c.get("scheme_id"),
            "source_url": c.get("source_url"),
            "section": c.get("section"),
            "section_title": c.get("section_title"),
        }
        fns = c.get("field_names", []) or []
        if fns:
            md["field_names"] = fns
        metadatas.append(md)

    print(f"Upserting {len(ids)} vectors into ChromaDB at {CHROMA_DIR}")
    # Chroma accepts embeddings as list of lists
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    # Save metadata for audit
    with METADATA_OUTPUT.open("w", encoding="utf-8") as f:
        json.dump({"count": len(ids), "collection": "mutual_fund_chunks"}, f, indent=2)

    print(f"Saved {len(ids)} vectors to ChromaDB (persist dir: {CHROMA_DIR})")


if __name__ == "__main__":
    main()

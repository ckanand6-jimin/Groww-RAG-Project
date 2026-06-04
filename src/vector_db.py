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
COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION", "mutual_fund_chunks")
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


def init_chroma(persist_dir: Path = CHROMA_DIR):
    persist_dir.mkdir(parents=True, exist_ok=True)
    settings = Settings(persist_directory=str(persist_dir), is_persistent=True)
    client = chromadb.Client(settings=settings)
    return client


def ensure_collection(client, name: str = COLLECTION_NAME):
    # get_or_create_collection will return existing or create new
    return client.get_or_create_collection(name=name)


def upsert_chunks_into_chroma(
    collection_name: str = COLLECTION_NAME,
    model_name: str = EMBEDDING_MODEL,
    force_refresh: bool = False,
):
    client = init_chroma()
    collection = ensure_collection(client, collection_name)
    count = collection.count() if hasattr(collection, "count") else None

    if force_refresh and count:
        print(f"Force refresh enabled. Recreating collection '{collection_name}'.")
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

        collection = client.get_or_create_collection(name=collection_name)
        count = 0

    if count:
        print(f"Collection '{collection_name}' already has {count} items. Upsert skipped.")
        return

    chunks = load_chunks()
    texts = [build_text_payload(c) for c in chunks]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    print("Computing embeddings for chunks...")
    embeddings = embed_texts(model, tokenizer, texts, device)

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

    print(f"Upserting {len(ids)} vectors into ChromaDB collection '{collection_name}'")
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    print("Upsert complete.")


def main():
    client = init_chroma()
    collection = ensure_collection(client)
    # If collection empty, populate from chunks
    try:
        existing = collection.count()
    except Exception:
        existing = None
    if existing:
        print(f"Collection '{collection.name}' has {existing} records. Nothing to do.")
    else:
        upsert_chunks_into_chroma(collection.name)


if __name__ == "__main__":
    main()

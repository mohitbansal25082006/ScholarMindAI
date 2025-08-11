# src/embeddings.py
import os
import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

# ------------------------------------------------------------------
# 0️⃣  Ensure identical Chroma settings across the whole project
# ------------------------------------------------------------------
os.environ["ANONYMIZED_TELEMETRY"] = "False"
DB_DIR = Path("data/embeddings")
DB_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(
    path=str(DB_DIR),
    settings=chromadb.config.Settings(anonymized_telemetry=False)
)

# ------------------------------------------------------------------
# 1️⃣  Encoder & collection
# ------------------------------------------------------------------
encoder = SentenceTransformer("all-MiniLM-L6-v2")

collection = client.get_or_create_collection(
    name="research_docs",
    metadata={"hnsw:space": "cosine"}
)

# ------------------------------------------------------------------
# 2️⃣  Helpers
# ------------------------------------------------------------------
CHUNKS_DIR = Path("data/processed")

def load_chunks():
    """Read all *_chunks.json files and return list[dict]."""
    chunks = []
    for file in CHUNKS_DIR.glob("*_chunks.json"):
        data = json.loads(file.read_text(encoding="utf-8"))
        chunks.extend(data)
    return chunks

def embed_and_store(chunks):
    """Embed texts and upsert into ChromaDB."""
    if not chunks:
        print("⚠️  No chunks to embed.")
        return

    ids = [f"{c['doc_id']}__{i}" for i, c in enumerate(chunks)]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {"doc_id": c["doc_id"], "page": c["page"], "citation": f"{c['doc_id']} p.{c['page']}"}
        for c in chunks
    ]

    embeddings = encoder.encode(texts, show_progress_bar=True).tolist()
    collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
    print(f"✅ Stored {len(chunks)} vectors in ChromaDB")

# ------------------------------------------------------------------
# 3️⃣  CLI convenience
# ------------------------------------------------------------------
if __name__ == "__main__":
    embed_and_store(load_chunks())
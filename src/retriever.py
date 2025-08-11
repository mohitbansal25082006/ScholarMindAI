# src/retriever.py
import os
import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Prevent telemetry + reuse identical settings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
DB_DIR = "data/embeddings"

client = chromadb.PersistentClient(
    path=DB_DIR,
    settings=chromadb.config.Settings(anonymized_telemetry=False)
)

EMBED = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

langchain_chroma = Chroma(
    client=client,
    collection_name="research_docs",
    embedding_function=EMBED
)

def retriever():
    return langchain_chroma.as_retriever(search_kwargs={"k": 3})

if __name__ == "__main__":
    docs = retriever().invoke("AI biology")
    print("Retrieved", len(docs), "chunks")
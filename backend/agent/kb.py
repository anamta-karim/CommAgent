import os
import glob
import chromadb

KB_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "kb_seed")

_collection = chromadb.PersistentClient(path="./chroma_kb").get_or_create_collection("faq_kb")

def refresh_index():
    """Load FAQ content from local seed files and (re)build Chroma. Run once at startup."""
    for path in glob.glob(os.path.join(KB_DIR, "*.md")):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        for i, chunk in enumerate(chunks):
            _collection.upsert(ids=[f"{path}-{i}"], documents=[chunk])

def query(question: str, k: int = 3) -> list[str]:
    return _collection.query(query_texts=[question], n_results=k)["documents"][0]
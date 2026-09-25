"""
kb.py — Fetch Notion KB pages, chunk text, embed into Chroma, query it.
"""
import os
from notion_client import Client
import chromadb
from chromadb.utils import embedding_functions

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_KB_PAGE_ID = os.environ["NOTION_KB_PAGE_ID"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # used only for embeddings

notion = Client(auth=NOTION_API_KEY)

# --- Chroma setup ---
chroma_client = chromadb.PersistentClient(path="./chroma_store")

# Use a free local embedding function so you don't burn an extra API key.
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="commagent_kb", embedding_function=embed_fn
)


def _extract_text_from_blocks(blocks) -> str:
    """Flatten a Notion block list into plain text."""
    text_parts = []
    for block in blocks:
        block_type = block.get("type")
        content = block.get(block_type, {})
        rich_text = content.get("rich_text", [])
        for rt in rich_text:
            plain = rt.get("plain_text", "")
            if plain:
                text_parts.append(plain)
    return "\n".join(text_parts)


def _get_page_title(page) -> str:
    props = page.get("properties", {})
    for prop in props.values():
        if prop.get("type") == "title":
            title_arr = prop.get("title", [])
            if title_arr:
                return title_arr[0].get("plain_text", "Untitled")
    return "Untitled"


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    """Simple word-based chunking."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start = end - overlap
    return [c for c in chunks if c.strip()]


def fetch_and_index_kb():
    """
    Fetch all child pages under NOTION_KB_PAGE_ID, chunk their text,
    and upsert into the Chroma collection. Call this once at startup
    (and optionally expose a /reindex endpoint for manual refresh).
    """
    children = notion.blocks.children.list(block_id=NOTION_KB_PAGE_ID)

    ids, documents, metadatas = [], [], []

    for block in children.get("results", []):
        if block.get("type") != "child_page":
            continue

        page_id = block["id"]
        page = notion.pages.retrieve(page_id=page_id)
        title = _get_page_title(page)

        page_blocks = notion.blocks.children.list(block_id=page_id)
        page_text = _extract_text_from_blocks(page_blocks.get("results", []))

        chunks = _chunk_text(page_text)
        for i, chunk in enumerate(chunks):
            ids.append(f"{page_id}_{i}")
            documents.append(chunk)
            metadatas.append({"source": title, "page_id": page_id})

    if not documents:
        print("WARNING: no KB content found — check page sharing/permissions.")
        return 0

    # Upsert: safe to call repeatedly, avoids duplicate growth on reindex
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    print(f"Indexed {len(documents)} chunks from {len(set(m['source'] for m in metadatas))} pages.")
    return len(documents)


def query_kb(question: str, top_k: int = 4):
    """
    Return top_k relevant chunks for a question, with source metadata.
    Used by nodes.py's retrieve step.
    """
    results = collection.query(query_texts=[question], n_results=top_k)

    chunks = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, meta, dist in zip(docs, metas, distances):
        chunks.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "distance": dist,  # lower = more relevant; useful for critique's confidence check
        })
    return chunks
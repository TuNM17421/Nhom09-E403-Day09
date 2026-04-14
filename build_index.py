"""
build_index.py — Tạo ChromaDB index từ documents trong data/docs/
Chạy: python build_index.py
"""

import os
import re
import chromadb
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = os.path.join(os.path.dirname(__file__), "data", "docs")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "day09_docs")


def split_by_sections(text: str, source: str) -> list[dict]:
    """Chia document thành chunks theo section headers (===)."""
    sections = re.split(r"\n(?===)", text)
    chunks = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Mỗi section là 1 chunk, kèm metadata source
        chunks.append({
            "text": section,
            "source": source,
        })

    return chunks


def build_index():
    # 1. Đọc tất cả docs
    all_chunks = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = split_by_sections(text, source=filename)
        all_chunks.extend(chunks)
        print(f"  {filename}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {len(all_chunks)}")

    # 2. Tạo embeddings với SentenceTransformer
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [c["text"] for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=True).tolist()
        print("Embedding model: all-MiniLM-L6-v2 (offline)")
    except ImportError:
        print("sentence-transformers not installed, using OpenAI embeddings...")
        from openai import OpenAI
        client = OpenAI()
        texts = [c["text"] for c in all_chunks]
        response = client.embeddings.create(input=texts, model="text-embedding-3-small")
        embeddings = [item.embedding for item in response.data]
        print("Embedding model: text-embedding-3-small (OpenAI)")

    # 3. Lưu vào ChromaDB
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # Xóa collection cũ nếu có để rebuild
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted existing collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"chunk_{i:03d}" for i in range(len(all_chunks))]
    documents = [c["text"] for c in all_chunks]
    metadatas = [{"source": c["source"]} for c in all_chunks]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"\nChromaDB index built successfully!")
    print(f"  Path: {CHROMA_DB_PATH}")
    print(f"  Collection: {COLLECTION_NAME}")
    print(f"  Documents: {collection.count()}")


if __name__ == "__main__":
    print("=" * 50)
    print("Building ChromaDB Index")
    print("=" * 50)
    build_index()

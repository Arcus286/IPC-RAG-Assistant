"""
retriever.py
Loads FAISS index + metadata and returns top-k relevant IPC sections for a query.
"""

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

FAISS_INDEX_PATH = "./faiss_index.bin"
METADATA_PATH = "./faiss_metadata.json"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Load once at module level
_model = None
_index = None
_metadata = None


def _get_model():
    global _model
    if _model is None:
        print("[retriever] Loading embedding model...")
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_index_and_metadata():
    global _index, _metadata
    if _index is None:
        print("[retriever] Loading FAISS index...")
        _index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
    return _index, _metadata


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """
    Embed the query and return the top-k most relevant IPC sections.

    Returns a list of dicts:
    [
      {
        "section_num": "302",
        "title": "Punishment for murder",
        "content": "...",
        "score": 0.87
      },
      ...
    ]
    """
    model = _get_model()
    index, metadata = _get_index_and_metadata()

    # Embed and normalize query
    query_embedding = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_embedding)

    # Search
    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        meta = metadata[idx]
        results.append({
            "section_num": meta["section_num"],
            "title": meta["title"],
            "content": meta["content"],
            "score": round(float(score), 4),
        })

    return results

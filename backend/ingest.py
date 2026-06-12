"""
ingest.py
Run once to parse the IPC PDF, chunk by section, embed, and store in FAISS index.
Usage: python ingest.py --pdf path/to/ipc.pdf
"""

import re
import json
import argparse
import pdfplumber
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ── Config ────────────────────────────────────────────────────────────────────
FAISS_INDEX_PATH = "./faiss_index.bin"
METADATA_PATH = "./faiss_metadata.json"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Regex to detect IPC section headers like "302." or "302A."
SECTION_PATTERN = re.compile(r"^\s*(\d{1,3}[A-Z]?)\.\s+(.+)", re.MULTILINE)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    print(f"[ingest] Reading PDF: {pdf_path}")
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in tqdm(pdf.pages, desc="Extracting pages"):
            text = page.extract_text()
            if text:
                full_text.append(text)
    return "\n".join(full_text)


def chunk_by_section(text: str) -> list[dict]:
    chunks = []
    matches = list(SECTION_PATTERN.finditer(text))

    for i, match in enumerate(matches):
        section_num = match.group(1).strip()
        title = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        if len(content) < 80:
            continue

        chunks.append({
            "section_id": f"IPC_S{section_num}",
            "section_num": section_num,
            "title": title,
            "content": content,
        })

    print(f"[ingest] Found {len(chunks)} IPC sections")
    return chunks


def embed_and_store(chunks: list[dict]):
    print(f"[ingest] Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    texts = [c["content"] for c in chunks]

    print("[ingest] Embedding sections (this may take a minute)...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index (Inner Product on normalized vectors = cosine similarity)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"[ingest] Saved FAISS index → {FAISS_INDEX_PATH}")

    # Save metadata separately (section_num, title, content)
    metadata = [
        {
            "section_num": c["section_num"],
            "title": c["title"],
            "content": c["content"],
        }
        for c in chunks
    ]
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"[ingest] Saved metadata → {METADATA_PATH}")

    print(f"[ingest] ✅ Done! {len(chunks)} sections stored.")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to IPC PDF file")
    args = parser.parse_args()

    raw_text = extract_text_from_pdf(args.pdf)
    chunks = chunk_by_section(raw_text)
    embed_and_store(chunks)

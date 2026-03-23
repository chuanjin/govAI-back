#!/usr/bin/env python3
"""
Seed script for GovAssist AI.
Reads markdown documents from /data, chunks them, generates embeddings,
and upserts into the Qdrant vector store.

Usage:
    python scripts/seed_vectordb.py           # Seed the database
    python scripts/seed_vectordb.py --dry-run  # Preview chunks without seeding
"""

import os
import sys
import hashlib
import argparse
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from govai.config import settings
from govai.services.embedding_service import generate_embedding
from govai.services.vector_store import ensure_collection, upsert_chunks, get_qdrant_client


DATA_DIR = Path(__file__).parent.parent / "data"


def read_markdown_files() -> list[dict]:
    """Read all markdown files from the data directory."""
    documents = []
    for md_file in sorted(DATA_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        # Extract metadata from the markdown
        title = ""
        source_url = ""
        agency = ""

        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("- URL:"):
                source_url = line.split("URL:", 1)[1].strip()
            elif line.startswith("- Agency:"):
                agency = line.split("Agency:", 1)[1].strip()

        documents.append({
            "path": str(md_file),
            "title": title,
            "source_url": source_url,
            "agency": agency,
            "content": content,
        })

    return documents


def chunk_document(doc: dict, chunk_size: int = 800, overlap: int = 100) -> list[dict]:
    """
    Split a document into chunks by section headers.
    Each chunk retains metadata for source attribution.
    """
    content = doc["content"]
    sections = []
    current_section = ""
    current_header = doc["title"]

    for line in content.split("\n"):
        if line.startswith("## ") and current_section.strip():
            sections.append({
                "section": current_header,
                "content": current_section.strip(),
            })
            current_header = line[3:].strip()
            current_section = line + "\n"
        elif line.startswith("### "):
            # Sub-sections: append to current but track
            current_section += line + "\n"
        else:
            current_section += line + "\n"

    # Don't forget the last section
    if current_section.strip():
        sections.append({
            "section": current_header,
            "content": current_section.strip(),
        })

    chunks = []
    for section in sections:
        text = section["content"]
        # If section is small enough, keep as one chunk
        if len(text) <= chunk_size * 4:  # Rough char estimate
            chunk_id = hashlib.md5(
                f"{doc['title']}:{section['section']}".encode()
            ).hexdigest()
            chunks.append({
                "id": chunk_id,
                "content": text,
                "title": doc["title"],
                "source_url": doc["source_url"],
                "section": section["section"],
                "language": "en",
            })
        else:
            # Split large sections into smaller chunks
            words = text.split()
            chunk_words = []
            word_count = 0
            part = 0

            for word in words:
                chunk_words.append(word)
                word_count += 1
                if word_count >= chunk_size // 5:  # ~5 chars per word
                    chunk_text = " ".join(chunk_words)
                    chunk_id = hashlib.md5(
                        f"{doc['title']}:{section['section']}:p{part}".encode()
                    ).hexdigest()
                    chunks.append({
                        "id": chunk_id,
                        "content": chunk_text,
                        "title": doc["title"],
                        "source_url": doc["source_url"],
                        "section": section["section"],
                        "language": "en",
                    })
                    # Keep overlap
                    overlap_words = chunk_words[-overlap // 5:] if overlap else []
                    chunk_words = overlap_words
                    word_count = len(chunk_words)
                    part += 1

            if chunk_words:
                chunk_text = " ".join(chunk_words)
                chunk_id = hashlib.md5(
                    f"{doc['title']}:{section['section']}:p{part}".encode()
                ).hexdigest()
                chunks.append({
                    "id": chunk_id,
                    "content": chunk_text,
                    "title": doc["title"],
                    "source_url": doc["source_url"],
                    "section": section["section"],
                    "language": "en",
                })

    return chunks


async def seed(dry_run: bool = False):
    """Main seeding function."""
    print("📄 Reading documents from data directory...")
    documents = read_markdown_files()
    print(f"   Found {len(documents)} documents")

    print("\n✂️  Chunking documents...")
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
        print(f"   {doc['title']}: {len(chunks)} chunks")

    print(f"\n   Total chunks: {len(all_chunks)}")

    if dry_run:
        print("\n🔍 DRY RUN — Preview of chunks:")
        for i, chunk in enumerate(all_chunks):
            print(f"\n--- Chunk {i+1} ---")
            print(f"   Title: {chunk['title']}")
            print(f"   Section: {chunk['section']}")
            print(f"   Source: {chunk['source_url']}")
            print(f"   Content length: {len(chunk['content'])} chars")
            print(f"   Preview: {chunk['content'][:120]}...")
        print(f"\n✅ Dry run complete. {len(all_chunks)} chunks would be created.")
        return

    print("\n🗄️  Ensuring Qdrant collection exists...")
    ensure_collection()

    print("\n🧮 Generating embeddings (this may take a moment)...")
    embeddings = []
    for i, chunk in enumerate(all_chunks):
        print(f"   Embedding chunk {i+1}/{len(all_chunks)}...", end="\r")
        embedding = await generate_embedding(chunk["content"])
        embeddings.append(embedding)
    print(f"   Generated {len(embeddings)} embeddings          ")

    print("\n📥 Upserting into Qdrant...")
    upsert_chunks(all_chunks, embeddings)

    print(f"\n✅ Successfully seeded {len(all_chunks)} chunks into Qdrant!")


def main():
    parser = argparse.ArgumentParser(description="Seed GovAssist AI vector database")
    parser.add_argument("--dry-run", action="store_true", help="Preview chunks without seeding")
    args = parser.parse_args()

    asyncio.run(seed(dry_run=args.dry_run))


if __name__ == "__main__":
    main()

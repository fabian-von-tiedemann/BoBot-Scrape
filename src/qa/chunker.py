"""
Document chunking utilities for semantic retrieval.

Splits markdown documents into overlapping token chunks while
preserving section context for citation references.
"""
import re
from dataclasses import dataclass
from pathlib import Path

import tiktoken
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn


@dataclass
class DocumentChunk:
    """A chunk of a document with metadata for retrieval."""
    content: str  # Chunk text
    document_path: str  # Relative path: category/filename.md
    section: str  # Nearest markdown heading, empty if none
    chunk_index: int  # Position within document
    token_count: int  # Number of tokens in chunk


def extract_section_heading(text: str) -> str:
    """
    Extract the last markdown heading from text.

    Looks for lines starting with # and returns the last one found,
    which represents the most recent section context.

    Args:
        text: Text to search for headings

    Returns:
        Last heading text found, or empty string if none
    """
    headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    return headings[-1] if headings else ""


def chunk_document(
    document_path: Path,
    chunk_size: int = 512,
    overlap: int = 128,
    encoding_name: str = "cl100k_base"
) -> list[DocumentChunk]:
    """
    Split a document into overlapping token chunks.

    Uses tiktoken for accurate token counting and creates chunks
    with overlap to preserve context across boundaries.

    Args:
        document_path: Path to the markdown document
        chunk_size: Maximum tokens per chunk (default 512)
        overlap: Token overlap between chunks (default 128)
        encoding_name: Tiktoken encoding to use (default cl100k_base)

    Returns:
        List of DocumentChunk with content and metadata
    """
    enc = tiktoken.get_encoding(encoding_name)

    try:
        with open(document_path, encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return []

    if not content.strip():
        return []

    # Skip YAML frontmatter (between --- markers)
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end + 3:].strip()

    if not content:
        return []

    # Tokenize content
    tokens = enc.encode(content)

    if not tokens:
        return []

    # Calculate relative document path (category/filename.md)
    # Handle both cases: document in category folder or standalone
    try:
        # Try to get parent folder as category
        category = document_path.parent.name
        rel_path = f"{category}/{document_path.name}"
    except Exception:
        rel_path = document_path.name

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)

        # Extract nearest section heading from chunk text
        section = extract_section_heading(chunk_text)

        chunks.append(DocumentChunk(
            content=chunk_text,
            document_path=rel_path,
            section=section,
            chunk_index=chunk_index,
            token_count=len(chunk_tokens)
        ))

        # Move start position with overlap
        start += chunk_size - overlap
        chunk_index += 1

    return chunks


def chunk_all_documents(
    documents_dir: Path,
    chunk_size: int = 512,
    overlap: int = 128
) -> list[DocumentChunk]:
    """
    Chunk all markdown documents in a directory recursively.

    Finds all .md files and processes them with progress tracking.

    Args:
        documents_dir: Root directory containing markdown files
        chunk_size: Maximum tokens per chunk
        overlap: Token overlap between chunks

    Returns:
        Flat list of all chunks from all documents
    """
    # Find all markdown files
    md_files = sorted(documents_dir.rglob("*.md"))

    if not md_files:
        return []

    all_chunks: list[DocumentChunk] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Chunking documents...", total=len(md_files))

        for md_file in md_files:
            chunks = chunk_document(md_file, chunk_size=chunk_size, overlap=overlap)
            all_chunks.extend(chunks)
            progress.advance(task)

    return all_chunks

"""
Swedish semantic retriever using FAISS and KBLab SBERT.

Provides efficient similarity search over document chunks
using Swedish-optimized sentence embeddings.
"""
import json
import logging
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from .chunker import DocumentChunk

logger = logging.getLogger(__name__)


class SwedishRetriever:
    """
    Semantic retriever using Swedish SBERT embeddings and FAISS index.

    Uses KBLab/sentence-bert-swedish-cased for Swedish-optimized
    sentence embeddings and FAISS IndexFlatIP for efficient
    cosine similarity search.
    """

    MODEL_NAME = "KBLab/sentence-bert-swedish-cased"

    def __init__(self, index_dir: Path):
        """
        Initialize retriever with index storage directory.

        Args:
            index_dir: Directory for storing/loading FAISS index and metadata
        """
        self.index_dir = Path(index_dir)
        self.model = SentenceTransformer(self.MODEL_NAME)
        self.index: faiss.IndexFlatIP | None = None
        self.chunks_meta: list[dict] = []

    def build_index(self, chunks: list[DocumentChunk]) -> None:
        """
        Build FAISS index from document chunks.

        Generates embeddings for all chunks, normalizes them for
        cosine similarity, and creates a FAISS IndexFlatIP index.
        Saves index and metadata to disk.

        Args:
            chunks: List of DocumentChunk to index
        """
        if not chunks:
            logger.warning("No chunks provided for indexing")
            return

        # Generate embeddings with progress bar
        texts = [c.content for c in chunks]
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Normalize for cosine similarity (inner product after normalization)
        faiss.normalize_L2(embeddings)

        # Create index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        # Store metadata for each chunk
        self.chunks_meta = [
            {
                "content": c.content,
                "document_path": c.document_path,
                "section": c.section,
                "chunk_index": c.chunk_index
            }
            for c in chunks
        ]

        # Save to disk
        self.index_dir.mkdir(parents=True, exist_ok=True)
        index_path = self.index_dir / "chunks.index"
        meta_path = self.index_dir / "chunks_meta.json"

        faiss.write_index(self.index, str(index_path))
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(self.chunks_meta, f, ensure_ascii=False, indent=2)

        logger.info(f"Index saved: {len(chunks)} chunks to {self.index_dir}")

    def load_index(self) -> None:
        """
        Load existing FAISS index and metadata from disk.

        Raises:
            FileNotFoundError: If index files don't exist
        """
        index_path = self.index_dir / "chunks.index"
        meta_path = self.index_dir / "chunks_meta.json"

        if not index_path.exists():
            raise FileNotFoundError(f"Index not found: {index_path}")

        self.index = faiss.read_index(str(index_path))
        with open(meta_path, encoding='utf-8') as f:
            self.chunks_meta = json.load(f)

        logger.info(f"Index loaded: {len(self.chunks_meta)} chunks from {self.index_dir}")

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Retrieve top-k most relevant chunks for a query.

        Args:
            query: Query text to search for
            top_k: Number of results to return (default 5)

        Returns:
            List of dicts with content, document_path, section, score

        Raises:
            RuntimeError: If index not loaded or built
        """
        if self.index is None:
            raise RuntimeError("Index not loaded. Call build_index() or load_index() first.")

        # Embed and normalize query
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)

        # Search index
        scores, indices = self.index.search(query_embedding, top_k)

        # Build results with metadata
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks_meta):
                result = self.chunks_meta[idx].copy()
                result["score"] = float(score)
                results.append(result)

        return results

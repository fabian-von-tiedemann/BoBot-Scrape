"""
QA generation module for BoBot-Scrape.

Provides persona-based Q&A generation for care worker training,
including semantic retrieval for answer grounding.
"""
from .persona import Persona, load_personas
from .question import (
    GeneratedQuestion,
    QuestionBatch,
    QuestionEntry,
    generate_questions_for_document,
    process_documents_batch,
    deduplicate_questions,
    write_questions_yaml,
)
from .chunker import (
    DocumentChunk,
    chunk_document,
    chunk_all_documents,
)
from .retriever import SwedishRetriever

__all__ = [
    # Persona
    'Persona',
    'load_personas',
    # Question generation
    'GeneratedQuestion',
    'QuestionBatch',
    'QuestionEntry',
    'generate_questions_for_document',
    'process_documents_batch',
    'deduplicate_questions',
    'write_questions_yaml',
    # Chunking and retrieval
    'DocumentChunk',
    'chunk_document',
    'chunk_all_documents',
    'SwedishRetriever',
]

"""
QA generation module for BoBot-Scrape.

Provides persona-based Q&A generation for care worker training.
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

__all__ = [
    'Persona',
    'load_personas',
    'GeneratedQuestion',
    'QuestionBatch',
    'QuestionEntry',
    'generate_questions_for_document',
    'process_documents_batch',
    'deduplicate_questions',
    'write_questions_yaml',
]

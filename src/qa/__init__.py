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
from .answer import (
    Citation,
    GeneratedAnswer,
    QAEntry,
    generate_answer,
    create_qa_entry,
    generate_answers_batch,
)
from .validator import (
    SourceVerification,
    QualityAssessment,
    ValidationResult,
    verify_source,
    assess_quality,
    compute_composite_score,
    validate_qa_pair,
)

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
    # Answer generation
    'Citation',
    'GeneratedAnswer',
    'QAEntry',
    'generate_answer',
    'create_qa_entry',
    'generate_answers_batch',
    # Validation
    'SourceVerification',
    'QualityAssessment',
    'ValidationResult',
    'verify_source',
    'assess_quality',
    'compute_composite_score',
    'validate_qa_pair',
]

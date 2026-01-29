"""
Answer generation for QA pipeline.

Generates grounded answers with citations using Gemini API and
retrieved document chunks. Enforces klarsprak Swedish (B1 level)
with extraction-style responses that prefer quoting source text.
"""
import logging
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from .retriever import SwedishRetriever

logger = logging.getLogger(__name__)


class Citation(BaseModel):
    """A citation to a source document."""
    document: str = Field(
        description="Full document path, e.g., rutiner/handtvatt.md"
    )
    section: str = Field(
        description="Section heading if available, empty otherwise"
    )


class GeneratedAnswer(BaseModel):
    """A grounded answer with citations from Gemini."""
    answer: str = Field(
        description="Svar pa klarsprak svenska (B1-niva, max 15 ord per mening, aktiv form)"
    )
    citations: list[Citation] = Field(
        min_length=1,
        description="Kallor som stodjer svaret"
    )
    coverage: Literal["full", "partial", "none"] = Field(
        description="Hur val kallorna tackte fragan"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Konfidensgrad for svaret"
    )


class QAEntry(BaseModel):
    """Complete question-answer pair for output."""
    question: str
    answer: str
    citations: list[dict]  # [{document: str, section: str}]
    coverage: str  # full, partial, none
    confidence: float
    source_document: str  # Original question source
    section: str  # Original question section
    question_type: str
    persona: dict
    category: str
    generated_at: str


ANSWER_GENERATION_PROMPT = '''Du ar en erfaren kollega som ger korta, tydliga svar pa svenska.

## VIKTIGAST: Citera kallorna direkt

Du ska CITERA relevant text direkt fran kallorna nar det ar mojligt.
- FOREDRA direkta citat for fakta, procedurer och instruktioner
- Parafraser endast nar citat skulle bli for langa eller krangliga
- Inkludera alltid exakta formuleringar for doser, tider, regler och steg

## Klarsprakskrav

- Max 15 ord per mening
- Anvand aktiv form: "Du tvattar handerna" INTE "Handerna ska tvattas"
- Tilltala med "du" konsekvent
- Vanligt ordforrad, undvik facktermer om mojligt
- Om fackterm anvands, forklara kort

## Citering

- Varje pastende maste ha en kallhanvisning: [source:dokument.md#sektion]
- Om sektionen saknas, ange bara dokumentet: [source:dokument.md]
- Placera kallhanvisning direkt efter citatet eller pastaendet
- Flera kallor: "X [source:doc1.md]. Y [source:doc2.md]."

## Svarsformat

- Kort svar: 1-4 meningar (langre om nodvandigt for att inkludera viktiga citat)
- Borja med det viktigaste
- Om kallorna inte besvarar fragan helt: "Kallorna beskriver X men inte Y."

## Fraga
{question}

## Kallor
{sources}

Ge ett grundat svar med direkta citat fran kallorna:
'''


def generate_answer(
    question: str,
    retrieved_chunks: list[dict],
    delay: float = 0.2
) -> GeneratedAnswer | None:
    """
    Generate a grounded answer using Gemini with structured output.

    Args:
        question: The question to answer
        retrieved_chunks: List of retrieved chunks with content, document_path, section
        delay: Delay in seconds after API call (rate limit awareness)

    Returns:
        GeneratedAnswer with answer, citations, coverage, confidence, or None on failure
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set - cannot generate answer")
        return None

    if not retrieved_chunks:
        logger.warning("No retrieved chunks provided for answer generation")
        return None

    # Format sources for prompt with clear source references
    sources_text = ""
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_ref = chunk["document_path"]
        if chunk.get("section"):
            source_ref += f"#{chunk['section'].lower().replace(' ', '-')}"
        sources_text += f"\n### Kalla {i}: {source_ref}\n{chunk['content']}\n"

    prompt = ANSWER_GENERATION_PROMPT.format(
        question=question,
        sources=sources_text
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedAnswer,
            )
        )

        if delay > 0:
            time.sleep(delay)

        # Log token usage if available
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            logger.debug(
                f"Gemini tokens - prompt: {response.usage_metadata.prompt_token_count}, "
                f"response: {response.usage_metadata.candidates_token_count}"
            )

        return response.parsed

    except ImportError as e:
        logger.error(f"google-genai package not installed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Answer generation failed: {e}")
        return None


def create_qa_entry(
    question_entry: dict,
    answer: GeneratedAnswer
) -> QAEntry:
    """
    Combine Phase 28 question with generated answer into full QA entry.

    Args:
        question_entry: Question dict from questions.yaml
        answer: GeneratedAnswer from Gemini

    Returns:
        QAEntry with all metadata combined
    """
    return QAEntry(
        question=question_entry["question"],
        answer=answer.answer,
        citations=[c.model_dump() for c in answer.citations],
        coverage=answer.coverage,
        confidence=answer.confidence,
        source_document=question_entry["source_document"],
        section=question_entry["section"],
        question_type=question_entry["question_type"],
        persona=question_entry["persona"],
        category=question_entry["category"],
        generated_at=datetime.now().isoformat()
    )


def generate_answers_batch(
    questions: list[dict],
    retriever: SwedishRetriever,
    output_path: Path,
    max_workers: int = 5,
    delay: float = 0.2,
    limit: int | None = None
) -> int:
    """
    Generate answers for a batch of questions with retrieval and progress tracking.

    Args:
        questions: List of question dicts from questions.yaml categories
        retriever: SwedishRetriever with loaded index
        output_path: Path to write answers.yaml
        max_workers: Maximum parallel API calls
        delay: Delay in seconds after each API call
        limit: Optional limit on number of questions to process

    Returns:
        Number of QA pairs successfully generated
    """
    # Apply limit if specified
    if limit:
        questions = questions[:limit]

    all_qa_entries: list[QAEntry] = []
    failed_count = 0

    def process_single(q: dict) -> QAEntry | None:
        """Process a single question: retrieve + generate answer."""
        nonlocal failed_count
        try:
            # Retrieve relevant chunks
            chunks = retriever.retrieve(q["question"], top_k=5)
            if not chunks:
                logger.debug(f"No chunks retrieved for: {q['question'][:50]}...")
                return None

            # Generate answer
            answer = generate_answer(q["question"], chunks, delay=delay)
            if not answer:
                return None

            return create_qa_entry(q, answer)

        except Exception as e:
            logger.warning(f"Failed to process question: {e}")
            failed_count += 1
            return None

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Generating answers...", total=len(questions))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(process_single, questions):
                if result:
                    all_qa_entries.append(result)
                progress.advance(task)

    # Group by category
    by_category: dict[str, list[dict]] = defaultdict(list)
    for entry in all_qa_entries:
        by_category[entry.category].append(entry.model_dump())

    # Build output structure
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_qa_pairs": len(all_qa_entries),
        "questions_processed": len(questions),
        "categories": dict(by_category)
    }

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            output, f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )

    logger.info(f"Wrote {len(all_qa_entries)} QA pairs to {output_path}")

    if failed_count > 0:
        logger.warning(f"Failed to generate {failed_count} answers")

    return len(all_qa_entries)

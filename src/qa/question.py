"""
Question generation for QA pipeline.

Generates persona-driven questions from documents using Gemini API
with structured output. Questions are designed to sound like real
care workers asking colleagues for help.
"""
import logging
import os
import random
import time
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field

from .persona import Persona

logger = logging.getLogger(__name__)


class GeneratedQuestion(BaseModel):
    """A question generated from a document by Gemini."""
    question: str = Field(
        description="Fragan pa svenska, konversationell ton"
    )
    question_type: Literal["factual", "procedural", "situational", "clarification"] = Field(
        description="Typ av fraga"
    )
    section_reference: str = Field(
        description="Dokumentsektion som fragan handlar om"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Konfidensgrad 0-1 for fragequalitet"
    )


class QuestionBatch(BaseModel):
    """Batch of questions from one document."""
    questions: list[GeneratedQuestion] = Field(
        min_length=3, max_length=5,
        description="3-5 fragor fran dokumentet"
    )


class QuestionEntry(BaseModel):
    """Full question entry for YAML output with complete metadata."""
    question: str
    source_document: str  # Relative path: category/filename.md
    section: str
    question_type: str
    persona: dict  # Full persona details: roll, erfarenhet, situation, sprakbakgrund
    confidence: float
    category: str  # Document category folder name
    generated_at: str  # ISO timestamp


QUESTION_GENERATION_PROMPT = '''Du ar en expert pa att generera fragor for utbildning av vardpersonal.

## Persona
Du genererar fragor som om de stalldes av denna person:
- Roll: {roll}
- Erfarenhet: {erfarenhet}
- Situation: {situation}
- Svenskkunskaper: {sprakbakgrund}

## Instruktioner
Generera 3-5 fragor fran detta dokument som personan skulle stalla.

Fragorna ska:
- Vara pa naturlig svenska med konversationell ton
- Inkludera kontext/motivation ("Jag ar ny pa jobbet och undrar...", "Jag horde nagon saga...", "Jag ar osaker pa...")
- Vara praktiska och relevanta for vardagligt arbete
- Referera till specifika sektioner i dokumentet

Fragetyper:
- factual: "Vad galler for...?"
- procedural: "Hur gor man...?"
- situational: "Vad gor jag om...?"
- clarification: "Vad menas med...?"

## Dokument
Titel: {title}
Kategori: {category}

{document_content}

Generera fragor:
'''


def select_persona_for_document(
    document_path: Path,
    personas: list[Persona]
) -> Persona:
    """
    Select best-fit persona based on document characteristics.

    Uses simple heuristics to match persona to document content:
    - Basic/intro docs -> nyanstald persona
    - Night shift docs -> persona with natt situation
    - Default: random selection for variety
    """
    try:
        with open(document_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Could not read {document_path}: {e}")
        return random.choice(personas)

    text_lower = content.lower()

    # Beginner persona for basic/intro documents
    if any(term in text_lower for term in ['introduktion', 'nyanstall', 'grundlaggande', 'checklista']):
        nyanstald = next((p for p in personas if p.erfarenhet == 'nyanstald'), None)
        if nyanstald:
            return nyanstald

    # Night shift persona for relevant documents
    if any(term in text_lower for term in ['natt', 'jour', 'beredskap']):
        natt_persona = next((p for p in personas if 'natt' in p.situation.lower()), None)
        if natt_persona:
            return natt_persona

    # Default: random selection for variety
    return random.choice(personas)


def generate_questions_for_document(
    document_path: Path,
    persona: Persona,
    delay: float = 0.1
) -> list[QuestionEntry]:
    """
    Generate questions for a document using Gemini API.

    Args:
        document_path: Path to the markdown document
        persona: Persona to use for question generation
        delay: Delay in seconds after API call (rate limit awareness)

    Returns:
        List of QuestionEntry with full metadata, or empty list on failure
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set - cannot generate questions")
        return []

    # Read document
    try:
        with open(document_path, encoding='utf-8') as f:
            document_text = f.read()
    except Exception as e:
        logger.warning(f"Could not read {document_path}: {e}")
        return []

    if not document_text.strip():
        logger.warning(f"Empty document: {document_path}")
        return []

    # Extract metadata
    category = document_path.parent.name
    title = document_path.stem

    # Build prompt
    prompt = QUESTION_GENERATION_PROMPT.format(
        roll=persona.roll,
        erfarenhet=persona.erfarenhet,
        situation=persona.situation,
        sprakbakgrund=persona.sprakbakgrund,
        title=title,
        category=category,
        document_content=document_text
    )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuestionBatch,
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

        # Transform to QuestionEntry list
        batch = response.parsed
        if not batch or not batch.questions:
            logger.warning(f"No questions generated for {document_path}")
            return []

        # Build relative source path
        source_document = f"{category}/{document_path.name}"
        generated_at = datetime.now().isoformat()

        entries = []
        for q in batch.questions:
            entry = QuestionEntry(
                question=q.question,
                source_document=source_document,
                section=q.section_reference,
                question_type=q.question_type,
                persona={
                    "roll": persona.roll,
                    "erfarenhet": persona.erfarenhet,
                    "situation": persona.situation,
                    "sprakbakgrund": persona.sprakbakgrund,
                },
                confidence=q.confidence,
                category=category,
                generated_at=generated_at,
            )
            entries.append(entry)

        return entries

    except ImportError as e:
        logger.error(f"google-genai package not installed: {e}")
        return []
    except Exception as e:
        logger.warning(f"Question generation failed for {document_path}: {e}")
        return []


def process_documents_batch(
    documents: list[Path],
    personas: list[Persona],
    max_workers: int = 5,
    delay: float = 0.2
) -> list[QuestionEntry]:
    """
    Process documents in parallel with progress tracking.

    Args:
        documents: List of document paths to process
        personas: List of personas to select from
        max_workers: Maximum parallel API calls (conservative for rate limits)
        delay: Delay in seconds after each API call

    Returns:
        All generated questions flattened into a single list
    """
    from concurrent.futures import ThreadPoolExecutor
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

    all_questions: list[QuestionEntry] = []

    def process_single(doc_path: Path) -> list[QuestionEntry]:
        """Process a single document."""
        persona = select_persona_for_document(doc_path, personas)
        questions = generate_questions_for_document(doc_path, persona, delay=delay)
        return questions

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Generating questions...", total=len(documents))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(process_single, documents):
                all_questions.extend(result)
                progress.advance(task)

    return all_questions


def deduplicate_questions(
    questions: list[QuestionEntry],
    threshold: float = 0.85
) -> list[QuestionEntry]:
    """
    Remove questions that are too similar to earlier ones.

    Uses difflib.SequenceMatcher for string similarity comparison.
    Questions with similarity >= threshold are considered duplicates.

    Args:
        questions: List of questions to deduplicate
        threshold: Similarity threshold (0.0-1.0), default 0.85

    Returns:
        List of unique questions
    """
    unique: list[QuestionEntry] = []

    for q in questions:
        is_duplicate = False
        q_lower = q.question.lower()

        for existing in unique:
            ratio = SequenceMatcher(
                None,
                q_lower,
                existing.question.lower()
            ).ratio()
            if ratio >= threshold:
                is_duplicate = True
                logger.debug(f"Duplicate found (ratio={ratio:.2f}): {q.question[:50]}...")
                break

        if not is_duplicate:
            unique.append(q)

    return unique


def write_questions_yaml(
    questions: list[QuestionEntry],
    output_path: Path
) -> None:
    """
    Write questions to YAML file grouped by category.

    Output structure:
    - generated_at: ISO timestamp
    - total_questions: count
    - categories:
        CategoryName:
          - question: ...
            source_document: ...
            ...

    Args:
        questions: List of questions to write
        output_path: Path to output YAML file
    """
    # Group by category
    by_category: dict[str, list[dict]] = defaultdict(list)
    for q in questions:
        by_category[q.category].append(q.model_dump())

    output = {
        "generated_at": datetime.now().isoformat(),
        "total_questions": len(questions),
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

    logger.info(f"Wrote {len(questions)} questions to {output_path}")

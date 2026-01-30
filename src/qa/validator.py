"""
Two-stage validation pipeline for QA pairs.

Stage 1: Source verification - confirms answer content exists in cited documents
         using semantic similarity with LLM fallback for borderline cases.

Stage 2: Quality assessment - LLM-as-judge scores three dimensions:
         relevans, korrekthet, fullstandighet on 0-1 scale.

Combined with composite score for pass/fail decision.
"""
import logging
import os
import re
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SourceVerification(BaseModel):
    """Stage 1: Source verification result."""

    is_grounded: bool = Field(
        description="Whether answer content exists in cited sources"
    )
    similarity_score: float = Field(
        ge=0.0, le=1.0, description="Semantic similarity score"
    )
    reasoning: str = Field(description="Explanation of verification result")
    ungrounded_claims: list[str] = Field(
        default_factory=list, description="Claims not found in sources"
    )


class QualityAssessment(BaseModel):
    """Stage 2: LLM-as-judge quality scores."""

    relevans: float = Field(
        ge=0.0, le=1.0, description="How well answer addresses the question"
    )
    korrekthet: float = Field(
        ge=0.0, le=1.0, description="Factual accuracy of the answer"
    )
    fullstandighet: float = Field(
        ge=0.0, le=1.0, description="Completeness of the answer"
    )
    reasoning: str = Field(description="Explanation of quality assessment")


class ValidationResult(BaseModel):
    """Combined validation result for a QA pair."""

    passed: bool
    composite_score: float = Field(ge=0.0, le=1.0)
    source_verification: SourceVerification
    quality_assessment: QualityAssessment | None = None  # None if source verification failed
    failure_reason: str | None = None


class BorderlineVerification(BaseModel):
    """LLM response for borderline source verification."""

    is_supported: bool = Field(description="Whether the claim is supported by the source")
    reasoning: str = Field(description="Explanation of the verification")


def extract_claims(answer_text: str) -> list[str]:
    """
    Extract claims from answer text by splitting into sentences.

    Filters out trivial sentences (very short, only citations, etc.)

    Args:
        answer_text: The answer text to extract claims from

    Returns:
        List of claim sentences
    """
    # Remove citation references for cleaner sentence splitting
    clean_text = re.sub(r'\[source:[^\]]+\]', '', answer_text)

    # Split by sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', clean_text.strip())

    claims = []
    for sentence in sentences:
        sentence = sentence.strip()
        # Filter trivial sentences
        if len(sentence) < 10:  # Too short to be meaningful
            continue
        if sentence.lower().startswith(('se ', 'las mer')):  # References
            continue
        claims.append(sentence)

    return claims


def verify_borderline_claim(
    claim: str,
    chunk_content: str,
    api_key: str
) -> BorderlineVerification | None:
    """
    Use LLM to verify borderline claims (similarity 0.5-0.75).

    Args:
        claim: The claim to verify
        chunk_content: Source text to check against
        api_key: Gemini API key

    Returns:
        BorderlineVerification result or None on failure
    """
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f'''Bedöm om påståendet stöds av källtexten.

## Påstående
{claim}

## Källtext
{chunk_content}

Svara på om påståendet finns i eller stöds av källtexten.'''

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=BorderlineVerification,
            )
        )

        return response.parsed

    except Exception as e:
        logger.warning(f"Borderline verification failed: {e}")
        return None


def verify_source(
    answer_text: str,
    citations: list[dict],
    retriever: "SwedishRetriever",
    similarity_threshold: float = 0.75,
    borderline_threshold: float = 0.5
) -> SourceVerification:
    """
    Verify that answer content exists in cited sources.

    Uses semantic similarity for initial scoring with LLM fallback
    for borderline cases (scores between 0.5 and 0.75).

    Thresholds:
        - >= similarity_threshold (0.75): auto-pass
        - 0.5 to 0.75: LLM judge for borderline verification
        - < 0.5: auto-fail

    Args:
        answer_text: The answer to verify
        citations: List of citation dicts with document and section keys
        retriever: SwedishRetriever with loaded index
        similarity_threshold: Score for automatic pass (default 0.75)
        borderline_threshold: Minimum score for borderline check (default 0.5)

    Returns:
        SourceVerification with is_grounded, similarity_score, reasoning
    """
    # Extract cited document paths
    cited_docs = set()
    for citation in citations:
        doc = citation.get('document', '')
        cited_docs.add(doc)

    # Extract claims from answer
    claims = extract_claims(answer_text)

    if not claims:
        return SourceVerification(
            is_grounded=True,
            similarity_score=1.0,
            reasoning="No substantive claims to verify",
            ungrounded_claims=[]
        )

    # Score each claim against cited documents
    claim_scores = []
    ungrounded = []

    api_key = os.environ.get('GEMINI_API_KEY')

    for claim in claims:
        # Use retriever to find best matching chunk
        results = retriever.retrieve(claim, top_k=5)

        # Filter to chunks from cited documents
        relevant = [r for r in results if r.get('document_path', '') in cited_docs]

        if not relevant:
            # No match in cited docs - check all results
            if results:
                best_score = results[0]['score']
                claim_scores.append(best_score * 0.5)  # Penalty for non-cited source
                if best_score < borderline_threshold:
                    ungrounded.append(claim)
            else:
                claim_scores.append(0.0)
                ungrounded.append(claim)
            continue

        best_match = relevant[0]
        best_score = best_match['score']

        # Handle based on threshold
        if best_score >= similarity_threshold:
            # Auto-pass
            claim_scores.append(best_score)
        elif best_score >= borderline_threshold and api_key:
            # Borderline - use LLM judge
            verification = verify_borderline_claim(
                claim,
                best_match['content'],
                api_key
            )
            if verification and verification.is_supported:
                claim_scores.append(best_score + 0.1)  # Boost for LLM confirmation
            else:
                claim_scores.append(best_score)
                if best_score < 0.6:
                    ungrounded.append(claim)
        else:
            # Below borderline threshold - fail
            claim_scores.append(best_score)
            ungrounded.append(claim)

    # Compute average similarity
    avg_similarity = sum(claim_scores) / len(claim_scores) if claim_scores else 0.0
    avg_similarity = min(1.0, avg_similarity)  # Cap at 1.0

    # Determine if grounded
    is_grounded = avg_similarity >= borderline_threshold and len(ungrounded) == 0

    # Build reasoning
    if is_grounded:
        reasoning = f"All {len(claims)} claims verified with average similarity {avg_similarity:.2f}"
    elif ungrounded:
        reasoning = f"{len(ungrounded)} of {len(claims)} claims not grounded in cited sources"
    else:
        reasoning = f"Low similarity score ({avg_similarity:.2f}) indicates weak source grounding"

    return SourceVerification(
        is_grounded=is_grounded,
        similarity_score=avg_similarity,
        reasoning=reasoning,
        ungrounded_claims=ungrounded
    )

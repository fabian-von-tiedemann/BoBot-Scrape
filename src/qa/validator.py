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

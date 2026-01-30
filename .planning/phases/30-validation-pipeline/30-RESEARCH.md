# Phase 30: Validation Pipeline - Research

**Researched:** 2026-01-29
**Domain:** LLM-as-judge evaluation, source verification, hallucination detection
**Confidence:** HIGH

## Summary

The validation pipeline implements two-stage quality assurance for QA pairs: (1) source verification confirming answer content exists in cited documents, and (2) LLM-as-judge quality assessment scoring relevans, korrekthet, and fullstandighet. Research confirms the hybrid approach from CONTEXT.md (semantic similarity first, LLM judge for borderline cases) aligns with current best practices.

The existing codebase already has the infrastructure needed: SwedishRetriever with FAISS/KBLab embeddings for semantic similarity, and Gemini structured output patterns in both answer.py and gemini.py. The validation module should follow these established patterns.

**Primary recommendation:** Implement semantic similarity with threshold 0.75 for automatic pass, LLM judge for scores 0.5-0.75, automatic fail below 0.5. Use separate LLM calls for source verification and quality scoring to maintain clear separation of concerns.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Project)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sentence-transformers | existing | Swedish embeddings for semantic similarity | Already using KBLab/sentence-bert-swedish-cased |
| faiss-cpu | existing | Fast cosine similarity search | Already indexed 1100+ documents |
| google-genai | existing | LLM-as-judge via Gemini Flash | Already used in answer.py with structured output |
| pydantic | existing | Structured output schemas | Already used for QAEntry, GeneratedAnswer |

### Supporting (Already Available)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | existing | L2 normalization, score computation | Cosine similarity calculations |
| tiktoken | existing | Token counting for chunk alignment | Already used in chunker.py |
| rich | existing | Progress tracking | Already used in answer.py batch processing |

### No New Dependencies Needed
The existing stack fully supports the validation pipeline. No new libraries required.

**Installation:** N/A - all dependencies already present

## Architecture Patterns

### Recommended Project Structure
```
src/qa/
├── answer.py         # Existing - answer generation
├── retriever.py      # Existing - semantic retrieval
├── chunker.py        # Existing - document chunking
├── validator.py      # NEW - validation pipeline
└── __init__.py       # Update exports
```

### Pattern 1: Two-Stage Validation Pipeline
**What:** Sequential validation where Stage 1 (source verification) must pass before Stage 2 (quality assessment) runs
**When to use:** Always - reduces unnecessary LLM calls for clearly invalid pairs
**Example:**
```python
# Source: Existing pattern in answer.py
from pydantic import BaseModel, Field
from typing import Literal

class SourceVerification(BaseModel):
    """Stage 1: Source verification result."""
    is_grounded: bool = Field(description="Whether answer content exists in cited sources")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Semantic similarity score")
    reasoning: str = Field(description="Explanation of verification result")
    ungrounded_claims: list[str] = Field(default_factory=list, description="Claims not found in sources")

class QualityAssessment(BaseModel):
    """Stage 2: LLM-as-judge quality scores."""
    relevans: float = Field(ge=0.0, le=1.0, description="How well answer addresses the question")
    korrekthet: float = Field(ge=0.0, le=1.0, description="Factual accuracy of the answer")
    fullstandighet: float = Field(ge=0.0, le=1.0, description="Completeness of the answer")
    reasoning: str = Field(description="Explanation of quality assessment")

class ValidationResult(BaseModel):
    """Combined validation result for a QA pair."""
    passed: bool
    composite_score: float  # 0-1, weighted combination
    source_verification: SourceVerification
    quality_assessment: QualityAssessment | None  # None if source verification failed
    failure_reason: str | None
```

### Pattern 2: Semantic Similarity First
**What:** Use embeddings to compute cosine similarity before invoking LLM judge
**When to use:** Source verification stage - faster and cheaper than LLM for clear pass/fail
**Example:**
```python
# Source: Existing pattern in retriever.py
def verify_source_coverage(
    answer_text: str,
    cited_documents: list[str],
    retriever: SwedishRetriever,
    similarity_threshold: float = 0.75
) -> tuple[float, list[dict]]:
    """
    Check if answer claims are supported by cited documents.

    Uses existing FAISS index and KBLab embeddings.
    Returns (similarity_score, list of claim->source mappings).
    """
    # Split answer into claims (sentences)
    claims = extract_claims(answer_text)

    # For each claim, find best matching chunk from cited docs
    claim_scores = []
    for claim in claims:
        # Use existing retriever - already handles embedding + normalization
        results = retriever.retrieve(claim, top_k=3)
        # Filter to only cited documents
        relevant = [r for r in results if r['document_path'] in cited_documents]
        if relevant:
            claim_scores.append(relevant[0]['score'])
        else:
            claim_scores.append(0.0)

    return sum(claim_scores) / len(claim_scores) if claim_scores else 0.0
```

### Pattern 3: LLM-as-Judge with Chain-of-Thought
**What:** Request step-by-step reasoning before final scores for better reliability
**When to use:** Quality assessment stage and borderline source verification
**Example:**
```python
# Source: Best practices from research
QUALITY_ASSESSMENT_PROMPT = '''Du ar en erfaren granskare av QA-par for utbildningsmaterial.

Bedöm detta QA-par pa tre dimensioner. Ge forst din resonemang, sedan poang 0.0-1.0.

## Dimensioner

### Relevans (0.0-1.0)
Hur val svaret adresserar fragan:
- 1.0: Svar ar helt fokuserat pa fragan
- 0.7: Svar ar relevant men inkluderar onodigt material
- 0.4: Svar ar delvis relevant
- 0.0: Svar ar helt irrelevant

### Korrekthet (0.0-1.0)
Faktisk riktighet baserat pa kallorna:
- 1.0: Alla pastaenden ar korrekta enligt kallorna
- 0.7: Smarre felaktigheter eller oprecisa formuleringar
- 0.4: Betydande felaktigheter
- 0.0: Helt felaktigt eller motsager kallorna

### Fullstandighet (0.0-1.0)
Hur komplett svaret ar:
- 1.0: Alla relevanta aspekter tackta
- 0.7: De viktigaste aspekterna tackta
- 0.4: Delvis tackt, viktig information saknas
- 0.0: Mycket ofullstandigt

## Fraga
{question}

## Svar
{answer}

## Kallor (fran citerade dokument)
{sources}

Ge din bedomning med resonemang forst, sedan poang:
'''
```

### Anti-Patterns to Avoid
- **Scoring all dimensions in one LLM call with source verification:** Keep source verification and quality assessment separate. Mixed prompts reduce reliability.
- **Using granular 0-100 scales:** Binary or 3-5 point scales are more reliable. Use 0.0-1.0 continuous for fine-grained but interpret in bands.
- **Skipping semantic similarity:** Going straight to LLM judge is expensive and slow. Semantic similarity catches clear failures efficiently.
- **Not requesting reasoning:** Scores without reasoning are unreliable and hard to debug.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Claim extraction | Custom regex splitter | Sentence tokenization | Edge cases with citations, abbreviations |
| Semantic similarity | Custom cosine computation | Existing retriever.retrieve() | Already normalized, FAISS-optimized |
| Score aggregation | Simple average | Weighted composite with minimum thresholds | Some dimensions are critical (korrekthet) |
| Structured LLM output | Text parsing | Pydantic + Gemini structured output | Already working pattern in answer.py |

**Key insight:** The existing codebase has all the building blocks. The validator module orchestrates them rather than reimplementing.

## Common Pitfalls

### Pitfall 1: Threshold Tuning Without Data
**What goes wrong:** Setting similarity threshold too high (0.9) rejects valid paraphrases; too low (0.5) passes hallucinations
**Why it happens:** Paraphrased answers have lower similarity than direct quotes
**How to avoid:** Start with 0.75 threshold, LLM judge for 0.5-0.75 range, log all scores for later tuning
**Warning signs:** High false rejection rate, or hallucinations in output

### Pitfall 2: Citation Path Mismatch
**What goes wrong:** Citation document paths don't match chunk metadata paths
**Why it happens:** Answer.py uses [source:dokument.md#sektion] format; chunk metadata uses different path format
**How to avoid:** Normalize paths before comparison (strip leading dirs, handle encoding)
**Warning signs:** Source verification fails on obviously grounded answers

### Pitfall 3: Treating Partial Coverage as Failure
**What goes wrong:** Answers with coverage="partial" get rejected even when valid
**Why it happens:** Partial coverage is expected when question requires synthesis
**How to avoid:** Use existing confidence field as input; partial coverage with high similarity can pass
**Warning signs:** Good QA pairs with partial coverage all failing

### Pitfall 4: LLM Judge Bias Toward Verbosity
**What goes wrong:** Longer answers score higher on fullstandighet even when shorter is appropriate
**Why it happens:** LLMs associate more text with more complete
**How to avoid:** Prompt should explicitly state brevity is valued when appropriate
**Warning signs:** Short, correct answers scoring low on fullstandighet

### Pitfall 5: Not Logging Rejected Pairs
**What goes wrong:** Cannot debug why good pairs were rejected
**Why it happens:** Only tracking pass/fail without detailed reasoning
**How to avoid:** Write full validation result to qa_rejected.jsonl including all scores and reasoning
**Warning signs:** Unable to improve threshold tuning

## Code Examples

Verified patterns from existing codebase:

### Loading Existing Index and Documents
```python
# Source: retriever.py pattern
from pathlib import Path
from src.qa.retriever import SwedishRetriever

def load_validation_context(
    index_dir: Path = Path("qa/embeddings"),
    docs_dir: Path = Path("converted")
) -> tuple[SwedishRetriever, dict[str, str]]:
    """Load retriever and document content for validation."""
    retriever = SwedishRetriever(index_dir)
    retriever.load_index()

    # Load full document content for LLM judge context
    doc_contents = {}
    for md_file in docs_dir.rglob("*.md"):
        rel_path = f"{md_file.parent.name}/{md_file.name}"
        doc_contents[rel_path] = md_file.read_text(encoding='utf-8')

    return retriever, doc_contents
```

### Gemini Structured Output for Quality Assessment
```python
# Source: answer.py pattern, adapted for validation
from google import genai
from google.genai import types

def assess_quality(
    question: str,
    answer: str,
    sources: str,
    api_key: str
) -> QualityAssessment | None:
    """Run LLM-as-judge quality assessment."""
    client = genai.Client(api_key=api_key)

    prompt = QUALITY_ASSESSMENT_PROMPT.format(
        question=question,
        answer=answer,
        sources=sources
    )

    response = client.models.generate_content(
        model="gemini-3-flash-preview",  # Per CONTEXT.md decision
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QualityAssessment,
        )
    )

    return response.parsed
```

### Computing Composite Score
```python
# Source: Best practices from research
def compute_composite_score(
    source_score: float,
    quality: QualityAssessment,
    weights: dict[str, float] | None = None
) -> float:
    """
    Compute weighted composite score.

    Default weights prioritize korrekthet (accuracy is critical for training data).
    """
    if weights is None:
        weights = {
            "source": 0.3,      # Source grounding
            "relevans": 0.2,    # Relevance to question
            "korrekthet": 0.3,  # Factual accuracy (highest)
            "fullstandighet": 0.2  # Completeness
        }

    return (
        weights["source"] * source_score +
        weights["relevans"] * quality.relevans +
        weights["korrekthet"] * quality.korrekthet +
        weights["fullstandighet"] * quality.fullstandighet
    )
```

### Batch Validation with Progress
```python
# Source: answer.py batch pattern
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from concurrent.futures import ThreadPoolExecutor

def validate_batch(
    qa_pairs: list[dict],
    retriever: SwedishRetriever,
    doc_contents: dict[str, str],
    output_passed: Path,
    output_rejected: Path,
    threshold: float = 0.7,
    max_workers: int = 5
) -> dict:
    """
    Validate batch of QA pairs with progress tracking.

    Returns summary statistics.
    """
    passed = []
    rejected = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Validating QA pairs...", total=len(qa_pairs))

        for qa in qa_pairs:
            result = validate_single(qa, retriever, doc_contents)
            if result.composite_score >= threshold:
                passed.append({**qa, "validation": result.model_dump()})
            else:
                rejected.append({**qa, "validation": result.model_dump()})
            progress.advance(task)

    # Write outputs
    write_jsonl(output_passed, passed)
    write_jsonl(output_rejected, rejected)

    return {
        "total": len(qa_pairs),
        "passed": len(passed),
        "rejected": len(rejected),
        "pass_rate": len(passed) / len(qa_pairs) if qa_pairs else 0,
        "avg_score": sum(p["validation"]["composite_score"] for p in passed) / len(passed) if passed else 0
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Simple string matching | Semantic similarity with embeddings | 2023 | Catches paraphrases, handles Swedish |
| Single LLM score | Multi-dimension rubric scoring | 2024 | More reliable, debuggable |
| Binary pass/fail | Continuous 0-1 with thresholds | 2024 | Better for borderline cases |
| No reasoning output | Chain-of-thought reasoning required | 2025 | 10-15% reliability improvement |
| Single judge model | Generation and evaluation separation | 2025 | Reduces bias, clearer responsibility |

**Deprecated/outdated:**
- BLEU/ROUGE scores for semantic matching: Too focused on surface form, misses paraphrases
- Single "quality" score without dimensions: Unmaintainable, unclear what failed

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal semantic similarity threshold for Swedish**
   - What we know: 0.75-0.85 range is typical for English
   - What's unclear: KBLab Swedish model may have different score distributions
   - Recommendation: Start at 0.75, log all scores, tune after initial run

2. **Dimension weights for composite score**
   - What we know: Korrekthet most important for training data
   - What's unclear: Optimal balance between dimensions
   - Recommendation: Use suggested weights (korrekthet 0.3), allow override via config

3. **Retry logic for borderline cases**
   - What we know: CONTEXT.md marks this as Claude's discretion
   - What's unclear: Cost/benefit of retry vs simple rejection
   - Recommendation: Skip retry for v1.0, rejected pairs can be manually reviewed

## Sources

### Primary (HIGH confidence)
- Existing codebase: src/qa/answer.py, retriever.py, chunker.py - verified working patterns
- [Evidently AI LLM-as-a-Judge Guide](https://www.evidentlyai.com/llm-guide/llm-as-a-judge) - prompting best practices
- [Confident AI LLM Evaluation Metrics](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation) - faithfulness and correctness metrics
- [Google Gemini Structured Output Docs](https://ai.google.dev/gemini-api/docs/structured-output) - Pydantic integration

### Secondary (MEDIUM confidence)
- [Monte Carlo LLM-as-Judge Best Practices](https://www.montecarlodata.com/blog-llm-as-judge/) - threshold recommendations
- [RAGAS Semantic Similarity](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/semantic_similarity/) - scoring methodology
- [Sentence Transformers Documentation](https://www.sbert.net/) - cosine similarity patterns

### Tertiary (LOW confidence)
- WebSearch results on optimal thresholds - varies by domain, needs validation
- Dimension weighting recommendations - needs tuning for this specific use case

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - using existing project dependencies
- Architecture: HIGH - following established patterns in codebase
- Pitfalls: MEDIUM - based on general best practices, needs project-specific validation
- Thresholds: LOW - require tuning with actual data

**Research date:** 2026-01-29
**Valid until:** 2026-02-28 (30 days - stable domain)

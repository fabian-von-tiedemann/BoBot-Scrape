# Stack Research: QA Generation Pipeline

**Project:** BoBot-Scrape v5.0
**Researched:** 2026-01-24
**Overall Confidence:** HIGH (verified with official documentation)

## Executive Summary

The v5.0 QA generation pipeline can be built entirely on top of the existing stack (google-genai, Pydantic) with minimal new dependencies. Gemini's structured output via Pydantic is already proven in the codebase. For grounding answers, Gemini's embedding model (`gemini-embedding-001`) provides semantic similarity search without needing external vector databases. RAGAS offers optional quality metrics but adds complexity - a simpler two-stage validation using Gemini itself is recommended for this scale (~1100 docs, thousands of QA pairs).

## Recommended Stack

### Core Framework (Already Installed)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | >=3.11 | Runtime | Already in use, async support mature |
| google-genai | >=1.0.0 | LLM API | Already using for metadata, native Pydantic support |
| pydantic | >=2.0.0 | Schema validation | Already using for DocumentMetadata, structured output |
| python-dotenv | >=1.0.0 | Config | Already loading GEMINI_API_KEY |

### New Dependencies

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| numpy | >=1.24.0 | Cosine similarity | Lightweight, no heavy dependencies |

**That's it.** No vector database, no LangChain, no additional frameworks needed.

### Optional (Not Recommended for v5.0)

| Technology | Purpose | Why Not Now |
|------------|---------|-------------|
| ragas | Evaluation metrics | Overkill for initial generation; adds OpenAI dependency |
| chromadb/faiss | Vector storage | 1100 docs fits in memory; numpy cosine is sufficient |
| langchain | Orchestration | Adds abstraction layer we don't need |

## LLM Strategy

### Model Selection

| Task | Model | Rationale |
|------|-------|-----------|
| Question generation | gemini-3-flash-preview | Fast, cheap, good at following structured prompts |
| Answer generation | gemini-3-flash-preview | Same model, grounded via context injection |
| Validation | gemini-3-flash-preview | LLM-as-judge for faithfulness scoring |
| Embeddings | gemini-embedding-001 | Native Google model, 2048 token limit, 768 dimensions |

**Source:** [Gemini API Structured Output](https://ai.google.dev/gemini-api/docs/structured-output), [Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)

### Why Stay on Gemini

1. **Already integrated** - google-genai SDK already in requirements.txt
2. **Structured output works** - Pydantic schemas proven in src/ai/gemini.py
3. **Embeddings included** - Same SDK, same API key
4. **Consistent billing** - One provider, one quota to manage
5. **Swedish support** - Gemini handles Swedish well (proven in metadata generation)

## Embedding/Retrieval Strategy

### Approach: In-Memory Semantic Search

For ~1100 documents, a full vector database is unnecessary. Use:

1. **Pre-compute embeddings** for all document chunks at pipeline start
2. **Store in numpy array** (~3MB at 768 dimensions x 3000 chunks)
3. **Cosine similarity** for retrieval at generation time

### Implementation Pattern

```python
from google import genai
from google.genai import types
import numpy as np

client = genai.Client()

# Embed documents (once, at pipeline start)
def embed_documents(texts: list[str]) -> np.ndarray:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=768
        )
    )
    return np.array([e.values for e in result.embeddings])

# Retrieve relevant chunks
def find_relevant_chunks(query: str, doc_embeddings: np.ndarray,
                         texts: list[str], top_k: int = 3) -> list[str]:
    query_result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        )
    )
    query_embedding = np.array(query_result.embeddings[0].values)

    # Cosine similarity
    similarities = np.dot(doc_embeddings, query_embedding) / (
        np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [texts[i] for i in top_indices]
```

**Source:** [Gemini Embeddings Documentation](https://ai.google.dev/gemini-api/docs/embeddings)

### Chunking Strategy

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Chunk size | 500-800 tokens | Fits in embedding context (2048 limit) with margin |
| Overlap | 100 tokens | Preserves context at boundaries |
| Split on | Paragraph/section boundaries | Swedish documents have clear headers |

The existing markdown documents already have structure (headers, sections). Split on `##` headers first, then paragraphs if sections are too long.

## Pydantic Models for QA Generation

### Core Data Models

```python
from pydantic import BaseModel, Field
from typing import Literal

class Persona(BaseModel):
    """Who is asking the question."""
    role: Literal["underskoterska", "hemtjanst_personal", "nattjour",
                  "ny_medarbetare", "chef", "anhorig"]
    situation: str = Field(description="Specific stressful/urgent context")

class Question(BaseModel):
    """A generated question from a persona."""
    question_text: str = Field(description="Natural Swedish question")
    persona: Persona
    source_document: str = Field(description="Document filename that inspired question")
    question_type: Literal["fakta", "instruktion", "policy", "kontakt"]

class Answer(BaseModel):
    """A grounded answer with source reference."""
    answer_text: str = Field(description="Answer in Swedish, appropriate length")
    source_chunks: list[str] = Field(description="Exact text excerpts supporting answer")
    source_documents: list[str] = Field(description="Document filenames")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence")

class QAPair(BaseModel):
    """Complete validated QA pair."""
    id: str
    question: Question
    answer: Answer
    validation: "ValidationResult"

class ValidationResult(BaseModel):
    """Two-stage validation outcome."""
    source_verified: bool = Field(description="Answer is supported by cited sources")
    quality_score: float = Field(ge=0.0, le=1.0, description="Overall quality 0-1")
    issues: list[str] = Field(default_factory=list, description="Any problems found")
```

## Validation Approach

### Two-Stage Validation (Recommended)

**Stage 1: Source Verification**
- Check that `answer.source_chunks` actually contain information supporting `answer.answer_text`
- Use Gemini with a simple yes/no prompt:

```python
VERIFICATION_PROMPT = """
Given these source excerpts:
{source_chunks}

Does this answer accurately reflect the sources?
Answer: {answer_text}

Respond with JSON: {"verified": true/false, "issues": ["issue1", ...]}
"""
```

**Stage 2: Quality Assessment**
- LLM-as-judge for overall quality:
  - Completeness: Does it fully answer the question?
  - Clarity: Is it understandable for the persona?
  - Format: Appropriate length/structure for question type?

```python
QUALITY_PROMPT = """
Evaluate this QA pair for a {persona.role} in {persona.situation}:

Question: {question_text}
Answer: {answer_text}

Score 0-1 on:
- completeness: Does it fully answer the question?
- clarity: Is it clear for the target persona?
- format: Appropriate length and structure?

Respond with JSON: {"score": 0.0-1.0, "issues": ["issue1", ...]}
"""
```

### Why Not RAGAS

RAGAS is excellent for RAG evaluation but adds complexity:
- Requires separate embedding model configuration
- Designed for evaluating retrieval, not generating QA
- Adds langchain + openai dependencies
- Overkill for initial generation phase

**Consider RAGAS later** for evaluating the QA dataset quality after v5.0 ships.

**Source:** [RAGAS Documentation](https://docs.ragas.io/en/stable/), [All About Synthetic Data Generation](https://blog.ragas.io/all-about-synthetic-data-generation)

## Export Formats

### Primary: JSONL (Recommended)

```jsonl
{"id": "qa-001", "question": "Hur hanterar jag...", "answer": "...", "source_doc": "...", "persona": {...}}
{"id": "qa-002", "question": "Vad gäller för...", "answer": "...", "source_doc": "...", "persona": {...}}
```

**Why JSONL:**
- One QA pair per line, easy to stream/filter
- HuggingFace `datasets.load_dataset('json', data_files='qa.jsonl')` works directly
- Git-friendly (line-based diffs)
- Easy to append incrementally

**Source:** [HuggingFace Datasets JSONL Loading](https://huggingface.co/docs/datasets/v1.13.3/loading.html)

### Secondary: SQuAD Format (For Extractive QA)

If fine-tuning extractive QA models later:

```json
{
  "data": [{
    "title": "Hemtjanst",
    "paragraphs": [{
      "context": "Full document text...",
      "qas": [{
        "id": "qa-001",
        "question": "Hur hanterar jag mediciner?",
        "answers": [{"text": "...", "answer_start": 42}]
      }]
    }]
  }],
  "version": "2.0"
}
```

**When to use:** Only if training extractive QA models (BERT-style). Not needed for prompt-based evaluation.

**Source:** [SQuAD Format for Fine-Tuning](https://medium.com/@BH_Chinmay/converting-data-into-squad-format-for-fine-tuning-llm-models-229497b4e774)

### Tertiary: CSV (For Analysis)

```csv
id,question,answer,source_doc,persona_role,quality_score
qa-001,"Hur hanterar jag...","...","Hemtjanst/rutin.md","underskoterska",0.92
```

**When to use:** Quick analysis in Excel/pandas, stakeholder review.

## Not Recommended

### Do NOT Use

| Technology | Why Avoid |
|------------|-----------|
| OpenAI API | Different provider, different quota, Swedish not as strong |
| LangChain | Abstraction layer adds complexity without benefit at this scale |
| ChromaDB/Pinecone | Overkill for 1100 docs, numpy cosine is sufficient |
| RAGAS (for generation) | Designed for evaluation, not generation; adds dependencies |
| Multiple LLM providers | Stick with Gemini for consistency |

### Avoid These Patterns

| Anti-Pattern | Why |
|--------------|-----|
| Random chunk QA | Fails to create meaningful multi-doc questions |
| Ungrounded generation | Hallucination risk without source verification |
| Single validation pass | Two-stage catches more issues |
| Overly complex personas | 6 roles sufficient for care worker scenarios |

**Source:** [Synthetic Data Generation Best Practices](https://ydata.ai/resources/synthetic-qa-documents), [Confident AI Guide](https://www.confident-ai.com/blog/the-definitive-guide-to-synthetic-data-generation-using-llms)

## Integration Notes

### Fits Existing Pipeline

The QA generation pipeline integrates naturally with v4.0:

```
pipeline.py (existing)
    |
    +-- scrape.py (v1.0)
    +-- convert.py (v2.0) --> converted/*.md
    +-- index_kb.py (v2.5)
    +-- generate_prompts.py (v2.5)
    +-- combine_prompts.py (v2.5)
    |
    +-- generate_qa.py (NEW v5.0)
            |
            +-- Load converted/*.md
            +-- Pre-compute embeddings
            +-- For each document:
            |     +-- Generate personas
            |     +-- Generate questions
            |     +-- Retrieve context (embedding search)
            |     +-- Generate grounded answers
            |     +-- Validate (2-stage)
            +-- Export to qa_pairs.jsonl
```

### Reuse Existing Patterns

From `src/ai/gemini.py`:
- Pydantic structured output (already working)
- Batch processing with ThreadPoolExecutor (already implemented)
- Rate limiting with delay parameter (already in place)
- Graceful degradation on API errors (already handled)

### New Module Structure

```
src/
    qa/
        __init__.py
        models.py        # Pydantic models (Persona, Question, Answer, QAPair)
        embeddings.py    # Embedding + retrieval functions
        generator.py     # Question/answer generation
        validator.py     # Two-stage validation
        exporter.py      # JSONL/SQuAD/CSV export
```

### CLI Integration

```bash
# New pipeline stage
python generate_qa.py --input converted/ --output qa_pairs.jsonl

# Or integrated with pipeline.py
python pipeline.py --skip-scrape --generate-qa
```

## Installation

```bash
# Only one new dependency
pip install numpy>=1.24.0

# Updated requirements.txt
# Text extraction dependencies
pymupdf
python-docx

# AI dependencies
google-genai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# QA generation (v5.0)
numpy>=1.24.0
```

## Cost Estimation

| Operation | Model | Est. Calls | Est. Cost |
|-----------|-------|------------|-----------|
| Embed 1100 docs | gemini-embedding-001 | ~3000 chunks | ~$0.50 |
| Generate questions | gemini-3-flash-preview | ~5000 | ~$2.50 |
| Generate answers | gemini-3-flash-preview | ~5000 | ~$2.50 |
| Validation (2-stage) | gemini-3-flash-preview | ~10000 | ~$5.00 |
| **Total estimated** | | | **~$10-15** |

Note: Flash preview pricing is very low. This is a rough estimate for generating ~5000 QA pairs.

## Sources

### Official Documentation (HIGH confidence)
- [Gemini API Structured Output](https://ai.google.dev/gemini-api/docs/structured-output)
- [Gemini Embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- [Google GenAI Python SDK](https://github.com/googleapis/python-genai)
- [HuggingFace Datasets Loading](https://huggingface.co/docs/datasets/v1.13.3/loading.html)

### Framework Documentation (MEDIUM confidence)
- [RAGAS Testset Generation](https://docs.ragas.io/en/stable/getstarted/rag_testset_generation/)
- [SQuAD Format](https://medium.com/@BH_Chinmay/converting-data-into-squad-format-for-fine-tuning-llm-models-229497b4e774)

### Best Practices (MEDIUM confidence)
- [YData Synthetic QA](https://ydata.ai/resources/synthetic-qa-documents)
- [Confident AI Synthetic Data Guide](https://www.confident-ai.com/blog/the-definitive-guide-to-synthetic-data-generation-using-llms)
- [RAGAS Blog on Synthetic Data](https://blog.ragas.io/all-about-synthetic-data-generation)

### Research Papers (MEDIUM confidence)
- [LLM Hallucination Survey](https://dl.acm.org/doi/10.1145/3703155)
- [Dynamic-KGQA Framework](https://arxiv.org/abs/2503.05049)

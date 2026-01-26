# Phase 28: Question Generation - Research

**Researched:** 2026-01-25
**Domain:** LLM-based question generation, Gemini API structured outputs, batch processing
**Confidence:** HIGH

## Summary

Phase 28 implements persona-driven question generation from 1,143 markdown documents using the Gemini API. The research confirms that the existing Gemini integration pattern from `src/ai/gemini.py` should be extended with a new Pydantic model for questions. Questions are generated in Swedish with conversational tone, each tagged with persona, document source, section reference, and question type.

The standard approach uses Gemini's structured output feature (already proven in the codebase) with a new `GeneratedQuestion` Pydantic model. Batch processing follows the existing `batch_generate_metadata()` pattern with ThreadPoolExecutor. Deduplication uses stdlib `difflib.SequenceMatcher` (no new dependency needed) with a 0.85 similarity threshold. Output is YAML format using the existing PyYAML dependency.

**Primary recommendation:** Extend existing Gemini patterns from Phase 27 research; use ThreadPoolExecutor batch processing with Rich progress bars; output single YAML file with all questions grouped by document category.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| google-genai | >=1.0.0 | Gemini API calls | Already installed, proven in src/ai/gemini.py |
| pydantic | 2.12.5 | Structured output schemas | Already installed, used for response_schema |
| pyyaml | 6.0.3 | YAML output | Already installed, CONTEXT.md specifies YAML |
| difflib | stdlib | Text similarity/dedup | No new dependency, ratio() for question dedup |
| rich | 14.x | Progress bars | Phase 27 noted as optional, now required for batch |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| datetime | stdlib | Timestamps | Generation timestamp per question |
| concurrent.futures | stdlib | Parallel processing | ThreadPoolExecutor for batch API calls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| difflib | sentence-transformers | Better semantic similarity but adds heavy dependency (PyTorch) |
| ThreadPoolExecutor | asyncio | Async more complex; ThreadPoolExecutor already used in gemini.py |
| YAML output | JSON output | YAML chosen in CONTEXT.md for human readability |
| Single file output | Per-document files | Single file easier for manual review and dedup |

**Installation:**
```bash
# Core dependencies already installed
pip install rich  # Required for progress bars
```

## Architecture Patterns

### Recommended Project Structure
```
src/
└── qa/
    ├── __init__.py          # Add Question, generate_questions exports
    ├── persona.py           # Already exists from Phase 27
    └── question.py          # NEW: Question model and generation logic
config/
└── personas.yaml            # Already exists from Phase 27
qa/                          # NEW: Output directory
└── questions.yaml           # Single output file with all questions
generate_qa.py               # Extend CLI with question generation
```

### Pattern 1: GeneratedQuestion Pydantic Model
**What:** Structured output schema for Gemini to return questions
**When to use:** Every Gemini call for question generation
**Example:**
```python
# Source: Existing gemini.py pattern + Pydantic docs
from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime

class GeneratedQuestion(BaseModel):
    """A question generated from a document."""
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
```

### Pattern 2: Question Output Entry with Full Metadata
**What:** Complete question record for YAML output
**When to use:** Final output structure
**Example:**
```python
# Source: CONTEXT.md requirements
from pydantic import BaseModel
from datetime import datetime

class QuestionEntry(BaseModel):
    """Full question entry for output file."""
    question: str
    source_document: str  # Relative path: category/filename.md
    section: str
    question_type: str
    persona: dict  # Full persona details
    confidence: float
    category: str  # Document category for grouping
    generated_at: str  # ISO timestamp
```

### Pattern 3: Gemini Prompt for Question Generation
**What:** Structured prompt template for persona-driven questions
**When to use:** Each document processing call
**Example:**
```python
# Source: Gemini prompting best practices + CONTEXT.md requirements
QUESTION_GENERATION_PROMPT = '''
Du ar en expert pa att generera fragor for utbildning av vardpersonal.

## Persona
Du genererar fragor som om de stalldes av denna person:
- Roll: {persona.roll}
- Erfarenhet: {persona.erfarenhet}
- Situation: {persona.situation}
- Svenskkunskaper: {persona.sprakbakgrund}

## Instruktioner
Generera 3-5 fragor fran detta dokument som personan skulle stalla.

Fragorna ska:
- Vara pa naturlig svenska med konversationell ton
- Inkludera kontext/motivation ("Jag ar ny pa jobbet och undrar...")
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
```

### Pattern 4: Batch Processing with Progress
**What:** Process all documents with rate limiting and progress display
**When to use:** Main generation loop
**Example:**
```python
# Source: Rich docs + existing gemini.py batch_generate_metadata pattern
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import time

def process_documents_batch(
    documents: list[Path],
    personas: list[Persona],
    max_workers: int = 5,  # Conservative for rate limits
    delay: float = 0.2     # Rate limit buffer
) -> list[QuestionEntry]:
    """Process documents in parallel with progress tracking."""
    all_questions = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
    ) as progress:
        task = progress.add_task("Generating questions...", total=len(documents))

        def process_single(doc_path: Path) -> list[QuestionEntry]:
            # Select best-fit persona based on document
            persona = select_persona_for_document(doc_path, personas)
            questions = generate_questions_for_document(doc_path, persona)
            time.sleep(delay)  # Rate limit
            return questions

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(process_single, documents):
                all_questions.extend(result)
                progress.advance(task)

    return all_questions
```

### Pattern 5: Deduplication with difflib
**What:** Remove similar questions across documents
**When to use:** After all questions generated, before output
**Example:**
```python
# Source: Python difflib docs
from difflib import SequenceMatcher

def deduplicate_questions(
    questions: list[QuestionEntry],
    threshold: float = 0.85
) -> list[QuestionEntry]:
    """Remove questions that are too similar to earlier ones."""
    unique = []

    for q in questions:
        is_duplicate = False
        for existing in unique:
            ratio = SequenceMatcher(
                None,
                q.question.lower(),
                existing.question.lower()
            ).ratio()
            if ratio >= threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            unique.append(q)

    return unique
```

### Pattern 6: YAML Output with Category Grouping
**What:** Write questions to YAML file grouped by document category
**When to use:** Final output step
**Example:**
```python
# Source: PyYAML docs + CONTEXT.md requirements
import yaml
from collections import defaultdict

def write_questions_yaml(
    questions: list[QuestionEntry],
    output_path: Path
) -> None:
    """Write questions to YAML grouped by category."""
    # Group by category
    by_category = defaultdict(list)
    for q in questions:
        by_category[q.category].append(q.model_dump())

    output = {
        "generated_at": datetime.now().isoformat(),
        "total_questions": len(questions),
        "categories": dict(by_category)
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(
            output, f,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False
        )
```

### Anti-Patterns to Avoid
- **One API call per persona per document:** Don't multiply API calls; one call per document with best-fit persona
- **Per-document output files:** Don't create 1143 output files; single YAML for easy review
- **Semantic similarity with sentence-transformers:** Don't add heavy ML dependency; difflib sufficient for string-level dedup
- **Async without rate limiting:** Don't use asyncio.gather without delays; will hit rate limits
- **Generating without section references:** Don't skip source tracking; QGEN-03 requires it

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured LLM output | Regex parsing | Pydantic + response_schema | Gemini handles JSON structure |
| Progress display | Print statements | Rich progress bars | Smooth updates, no flicker |
| Text similarity | Edit distance | difflib.SequenceMatcher | Stdlib, handles "looks right" matching |
| Rate limiting | Manual sleep | ThreadPoolExecutor + delay | Already proven in gemini.py |
| YAML serialization | Manual formatting | yaml.dump() | Handles Unicode, nested structures |

**Key insight:** The codebase already has working patterns for Gemini batch processing with structured outputs. Extend, don't reinvent.

## Common Pitfalls

### Pitfall 1: Rate Limit 429 Errors
**What goes wrong:** Too many API calls hit Gemini rate limits
**Why it happens:** Free tier is 15 RPM for Flash models (as of Dec 2025)
**How to avoid:** Use conservative max_workers (5) and delay (0.2s), add exponential backoff
**Warning signs:** 429 HTTP errors, incomplete batches

### Pitfall 2: Inconsistent Persona Assignment
**What goes wrong:** Questions don't match persona's likely knowledge level
**Why it happens:** Random persona selection ignores document topic
**How to avoid:** Match persona to document content (e.g., beginner persona for basic procedures)
**Warning signs:** Expert questions from beginner persona

### Pitfall 3: Questions Missing Source References
**What goes wrong:** Generated questions can't be traced back to document sections
**Why it happens:** Prompt doesn't emphasize section citation
**How to avoid:** Include section_reference in Pydantic model, prompt asks for specific section
**Warning signs:** Empty or generic section references like "hela dokumentet"

### Pitfall 4: Swedish Quality Issues
**What goes wrong:** Questions sound robotic or use incorrect Swedish
**Why it happens:** Prompt doesn't specify conversational tone, lacks examples
**How to avoid:** Include few-shot examples of natural Swedish questions in prompt
**Warning signs:** Formal language, missing context/motivation phrases

### Pitfall 5: Deduplication Too Aggressive
**What goes wrong:** Legitimately different questions removed
**Why it happens:** Similarity threshold too low (e.g., 0.7)
**How to avoid:** Use 0.85 threshold, test on sample before full run
**Warning signs:** Two distinct questions about "handtvatt" merged because both contain the word

### Pitfall 6: Document Too Long for Context Window
**What goes wrong:** Gemini truncates or fails on very long documents
**Why it happens:** Some documents exceed context window
**How to avoid:** Chunk long documents, or summarize before question generation
**Warning signs:** Questions only reference first part of document

## Code Examples

Verified patterns from official sources:

### Complete Question Generation Function
```python
# Source: Existing gemini.py pattern + Gemini structured output docs
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal
import logging

logger = logging.getLogger(__name__)

class GeneratedQuestion(BaseModel):
    question: str
    question_type: Literal["factual", "procedural", "situational", "clarification"]
    section_reference: str
    confidence: float = Field(ge=0.0, le=1.0)

class QuestionBatch(BaseModel):
    questions: list[GeneratedQuestion] = Field(min_length=3, max_length=5)

def generate_questions(
    document_text: str,
    document_title: str,
    category: str,
    persona: Persona,
    delay: float = 0.1
) -> list[GeneratedQuestion] | None:
    """Generate questions for a document using Gemini."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set")
        return None

    try:
        client = genai.Client(api_key=api_key)

        prompt = QUESTION_GENERATION_PROMPT.format(
            persona=persona,
            title=document_title,
            category=category,
            document_content=document_text
        )

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=QuestionBatch,
            )
        )

        if delay > 0:
            time.sleep(delay)

        return response.parsed.questions

    except Exception as e:
        logger.warning(f"Question generation failed: {e}")
        return None
```

### Persona Selection Based on Document Content
```python
# Source: CONTEXT.md decision - best-fit persona
def select_persona_for_document(
    document_path: Path,
    personas: list[Persona]
) -> Persona:
    """Select best-fit persona based on document characteristics."""
    # Read document metadata from frontmatter
    with open(document_path, encoding='utf-8') as f:
        content = f.read()

    # Simple heuristics for persona selection
    text_lower = content.lower()

    # Beginner persona for basic/intro documents
    if any(term in text_lower for term in ['introduktion', 'nyanstall', 'grundlaggande', 'checklista']):
        return next((p for p in personas if p.erfarenhet == 'nyanstald'), personas[0])

    # Night shift persona for relevant documents
    if any(term in text_lower for term in ['natt', 'jour', 'beredskap']):
        return next((p for p in personas if 'natt' in p.situation.lower()), personas[0])

    # Default: cycle through personas for variety
    return random.choice(personas)
```

### Complete YAML Output Structure
```yaml
# qa/questions.yaml
generated_at: "2026-01-25T14:30:00"
total_questions: 4587
categories:
  Hemtjanst:
    - question: "Jag ar ny i hemtjansten och undrar - hur ofta ska arbetskladerna bytas?"
      source_document: "Hemtjanst/Rutin basal hygien arbetsklader.md"
      section: "Hur gor du?"
      question_type: "procedural"
      persona:
        roll: "underskoterska"
        erfarenhet: "nyanstald"
        situation: "forsta manaden i hemtjansten"
        sprakbakgrund: "native"
      confidence: 0.92
      category: "Hemtjanst"
      generated_at: "2026-01-25T14:25:12"
    # ... more questions
  Boendestod:
    # ... questions for this category
```

### CLI Extension for Question Generation
```python
# Source: Phase 27 CLI pattern
def main():
    args = parse_args()

    # Load personas (from Phase 27)
    personas = load_personas(args.personas)
    print(f"Loaded {len(personas)} personas")

    # Find all documents
    documents = list(args.input.rglob("*.md"))
    print(f"Found {len(documents)} documents")

    # Generate questions with progress
    questions = process_documents_batch(
        documents=documents,
        personas=personas,
        max_workers=5,
        delay=0.2
    )
    print(f"Generated {len(questions)} questions")

    # Deduplicate
    unique_questions = deduplicate_questions(questions, threshold=0.85)
    print(f"After dedup: {len(unique_questions)} unique questions")

    # Write output
    output_file = args.output / "questions.yaml"
    write_questions_yaml(unique_questions, output_file)
    print(f"Saved to {output_file}")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual JSON parsing | Pydantic response_schema | 2025 | Guaranteed structure |
| Sequential API calls | ThreadPoolExecutor batch | Current best practice | 3-5x faster |
| Print progress | Rich progress bars | 2020+ | Better UX |
| sentence-transformers dedup | difflib for simple text | Context-dependent | No heavy dependency |

**Deprecated/outdated:**
- `google-generativeai` package - use `google-genai>=1.0.0` instead
- Gemini Pro 1.0 - use `gemini-3-flash-preview` for best cost/performance
- Free tier 30 RPM - reduced to 15 RPM for Flash as of Dec 2025

## Open Questions

Things that couldn't be fully resolved:

1. **Document length threshold for chunking**
   - What we know: Very long documents may exceed context window
   - What's unclear: Exact token limit for gemini-3-flash-preview, whether chunking needed
   - Recommendation: Start without chunking, add if errors occur on long docs

2. **Confidence score calibration**
   - What we know: Model returns confidence 0-1
   - What's unclear: Whether model's self-reported confidence correlates with actual quality
   - Recommendation: Track confidence scores, validate manually on sample

3. **Optimal questions per document**
   - What we know: CONTEXT.md says 3-5, longer docs might warrant more
   - What's unclear: Exact threshold for "long document"
   - Recommendation: Start with 3-5, track document length vs useful questions

## Sources

### Primary (HIGH confidence)
- [Gemini API Structured Output Documentation](https://ai.google.dev/gemini-api/docs/structured-output) - Pydantic response_schema usage
- [Rich Progress Documentation](https://rich.readthedocs.io/en/stable/progress.html) - Progress bar patterns
- [Python difflib Documentation](https://docs.python.org/3/library/difflib.html) - SequenceMatcher for deduplication
- Existing codebase: `src/ai/gemini.py` - Proven Gemini integration pattern

### Secondary (MEDIUM confidence)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits) - Current free tier limits
- [Gemini Prompt Strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies) - Question generation best practices
- [Google Developers Blog on Batch Mode](https://developers.googleblog.com/scale-your-ai-workloads-batch-mode-gemini-api/) - Batch processing patterns

### Tertiary (LOW confidence)
- WebSearch results on persona prompting effectiveness - suggests detailed personas help but not verified with this specific use case

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing project dependencies, proven patterns
- Architecture: HIGH - Extending established codebase patterns
- Pitfalls: HIGH - Based on documented rate limits and Gemini behavior
- Deduplication: MEDIUM - difflib works but threshold needs tuning

**Research date:** 2026-01-25
**Valid until:** 2026-02-25 (Gemini API evolves quickly, rate limits may change)

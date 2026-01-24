# Architecture Research: QA Generation Pipeline

**Project:** BoBot-Scrape v5.0
**Domain:** Synthetic QA pair generation from municipal document knowledge base
**Researched:** 2026-01-24
**Overall confidence:** HIGH (builds on existing patterns, verified with current sources)

## Executive Summary

The QA generation pipeline should follow the existing ETL pattern established in v4.0, adding a new stage that operates on the `converted/` markdown documents. The pipeline reads documents with their frontmatter metadata, generates persona-driven questions, produces grounded answers with source references, validates quality, and exports to structured formats.

The recommended architecture uses a **three-phase generation process**: (1) Question generation from documents using personas, (2) Answer generation grounded in source documents, (3) Two-stage validation (source verification + quality assessment). This mirrors industry best practices for synthetic data generation while leveraging the existing Gemini integration patterns.

## Component Overview

```
                                    QA Generation Pipeline (New)
                                    ============================

    +-----------+     +-------------+     +-------------+     +------------+     +----------+
    | converted/| --> | Question    | --> | Answer      | --> | Validator  | --> | Exporter |
    | (1143 md) |     | Generator   |     | Generator   |     |            |     |          |
    +-----------+     +-------------+     +-------------+     +------------+     +----------+
          |                 |                   |                   |                  |
          |                 v                   v                   v                  v
          |           +----------+        +----------+        +----------+       +----------+
          |           | Persona  |        | Document |        | Source   |       | qa_pairs/|
          |           | Engine   |        | Retriever|        | Verifier |       | (JSON)   |
          |           +----------+        +----------+        +----------+       +----------+
          |                                     |                   |
          +-------------------------------------+-------------------+
                            Document context flows back

    Existing Pipeline (Reference)
    =============================
    scrape.py --> convert.py --> index_kb.py --> generate_prompts.py --> combine_prompts.py
```

### Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|-------|--------|
| **generate_qa.py** | CLI orchestrator for QA pipeline | converted/, personas config | qa_pairs/ |
| **src/qa/question_generator.py** | Generate questions from documents using personas | Document text + persona | List of questions |
| **src/qa/answer_generator.py** | Generate grounded answers with source references | Question + source documents | Answer with citations |
| **src/qa/validator.py** | Two-stage validation (source + quality) | QA pair + source documents | Validation result |
| **src/qa/exporter.py** | Export to JSON/JSONL formats | Validated QA pairs | File output |
| **src/qa/persona.py** | Persona definitions and selection | None | Persona config |

## Data Flow

### Stage 1: Document Selection and Persona Assignment

```
Input: converted/{verksamhet}/*.md (1143 documents)
       ↓
       Read frontmatter: category, subcategory, document_type, keywords, topics
       ↓
       Select appropriate personas based on document metadata
       ↓
Output: List of (document, persona) pairs for question generation
```

### Stage 2: Question Generation

```
Input: Document text + Persona (role + situation)
       ↓
       Gemini API call with persona-aware prompt
       ↓
       Generate 3-5 questions per document based on persona's realistic needs
       ↓
Output: List of questions with metadata:
        - question_text
        - persona_id
        - source_document_path
        - question_type (factual, procedural, situational)
```

### Stage 3: Answer Generation

```
Input: Question + Source document(s)
       ↓
       Retrieve relevant passages from source document
       ↓
       Gemini API call with grounding prompt
       ↓
       Generate answer with inline citations [source:filename.md]
       ↓
Output: Answer with:
        - answer_text
        - citations (list of source references)
        - answer_format (short, step-by-step, detailed)
        - confidence_score
```

### Stage 4: Validation

```
Input: QA pair + Source documents
       ↓
       Step 1: Source Verification
       - Check all citations exist in source documents
       - Verify answer content is traceable to sources
       - Flag hallucinated content
       ↓
       Step 2: Quality Assessment
       - Evaluate answer completeness
       - Check question-answer alignment
       - Score overall quality (1-5)
       ↓
Output: Validation result:
        - is_valid (bool)
        - source_verified (bool)
        - quality_score (1-5)
        - issues (list of problems)
```

### Stage 5: Export

```
Input: Validated QA pairs
       ↓
       Filter by quality threshold (e.g., quality_score >= 3)
       ↓
       Format for different use cases:
       - prompt_context.jsonl (for AI assistant context)
       - evaluation.jsonl (for model evaluation)
       - training.jsonl (for fine-tuning)
       ↓
Output: Structured files in qa_pairs/
```

## Integration with Existing Pipeline

### Option A: Extend pipeline.py (Recommended)

Add QA generation as a new optional stage in the existing pipeline:

```python
# In pipeline.py
parser.add_argument(
    "--generate-qa",
    action="store_true",
    help="Generate QA pairs from converted documents"
)
parser.add_argument(
    "--qa-output",
    type=str,
    default=None,
    help="Output directory for QA pairs (default: run_dir/qa_pairs)"
)

# After prompts stage, if --generate-qa:
if args.generate_qa:
    cmd = [
        python_exe, "generate_qa.py",
        "--input", str(converted_dir),
        "--output", str(qa_output_dir),
        "--batch-size", "50"
    ]
    success, duration = run_stage("QA Generation", cmd)
```

### Option B: Standalone CLI

Separate script that can run independently:

```bash
# After pipeline completes
python generate_qa.py --input converted/ --output qa_pairs/

# Or with run directory
python generate_qa.py --input runs/2026-01-24-1200/converted/ --output qa_pairs/
```

**Recommendation:** Start with Option B for development, migrate to Option A once stable.

### Directory Structure

```
BoBot-Scrape/
├── pipeline.py           # Existing orchestrator
├── generate_qa.py        # NEW: QA generation CLI
├── src/
│   ├── ai/
│   │   ├── gemini.py     # Existing Gemini integration
│   │   └── __init__.py
│   ├── qa/               # NEW: QA generation module
│   │   ├── __init__.py
│   │   ├── question_generator.py
│   │   ├── answer_generator.py
│   │   ├── validator.py
│   │   ├── exporter.py
│   │   └── persona.py
│   └── ...
├── converted/            # Input: 1143 markdown documents
├── qa_pairs/             # Output: Generated QA pairs
│   ├── raw/              # All generated pairs before validation
│   ├── validated/        # Pairs that passed validation
│   └── exports/          # Formatted exports
│       ├── prompt_context.jsonl
│       ├── evaluation.jsonl
│       └── training.jsonl
└── configs/
    └── personas.yaml     # Persona definitions
```

## Suggested Build Order

Based on dependencies between components:

### Phase 1: Core Infrastructure (Week 1)

**Dependencies:** None (builds on existing patterns)

1. **src/qa/persona.py** - Define persona model and load from YAML
   - Pydantic model for Persona (role, situation, question_styles)
   - 5-7 starter personas (underskoterska, enhetschef, nyanstald, etc.)
   - Persona selection logic based on document category

2. **src/qa/__init__.py** - Module setup

3. **configs/personas.yaml** - Initial persona definitions

### Phase 2: Question Generation (Week 1-2)

**Dependencies:** Phase 1 (personas)

4. **src/qa/question_generator.py** - Generate questions from documents
   - Reuse Gemini integration pattern from src/ai/gemini.py
   - Pydantic model for GeneratedQuestion
   - Batch generation with ThreadPoolExecutor (existing pattern)

5. **generate_qa.py** - CLI scaffold (question generation only)
   - Follow pattern from generate_prompts.py
   - --input, --output, --batch-size, --verbose flags

### Phase 3: Answer Generation (Week 2)

**Dependencies:** Phase 2 (questions)

6. **src/qa/answer_generator.py** - Generate grounded answers
   - Document retrieval (read source document content)
   - Answer generation with citation format
   - Pydantic model for GeneratedAnswer

7. Update generate_qa.py to include answer generation stage

### Phase 4: Validation (Week 2-3)

**Dependencies:** Phase 3 (answers)

8. **src/qa/validator.py** - Two-stage validation
   - Source verification (check citations exist)
   - Quality assessment (LLM-based scoring)
   - Pydantic model for ValidationResult

9. Update generate_qa.py to include validation stage

### Phase 5: Export and Integration (Week 3)

**Dependencies:** Phase 4 (validation)

10. **src/qa/exporter.py** - Export to structured formats
    - JSONL output with different schemas per use case
    - Quality filtering options

11. Pipeline integration (Option A) - Add to pipeline.py

### Phase 6: Scale Testing (Week 3-4)

**Dependencies:** Phase 5 (complete pipeline)

12. Run on full corpus (1143 documents)
13. Tune batch sizes and rate limiting
14. Quality review and persona refinement

## Storage/Output Structure

### Raw QA Pair Format (qa_pairs/raw/)

```json
{
  "id": "qa_001234",
  "source_document": "Hemtjanst/Mobiltelefonrutin.md",
  "category": "Hemtjanst",
  "subcategory": "Mobiltelefon",
  "persona": {
    "id": "underskoterska_stressad",
    "role": "Underskoterska",
    "situation": "Stressad under arbetspass, behover snabbt svar"
  },
  "question": {
    "text": "Vad gor jag om mobilen inte fungerar under ett besok?",
    "type": "procedural",
    "generated_at": "2026-01-24T10:30:00Z"
  },
  "answer": {
    "text": "Vid fel pa mobilen ska du forst gora felsokn. Om felet inte kan losas maste du gora en felanmalan vid det aktuella tillfallet. [source:Mobiltelefonrutin.md]",
    "citations": ["Mobiltelefonrutin.md#rad-66-69"],
    "format": "step-by-step",
    "confidence": 0.92
  },
  "validation": {
    "source_verified": true,
    "quality_score": 4,
    "is_valid": true,
    "issues": []
  }
}
```

### Export Formats

**prompt_context.jsonl** - For AI assistant context injection:
```json
{"question": "...", "answer": "...", "category": "Hemtjanst"}
```

**evaluation.jsonl** - For model evaluation (RAGAS-compatible):
```json
{"question": "...", "answer": "...", "contexts": ["..."], "ground_truth": "..."}
```

**training.jsonl** - For fine-tuning (instruction format):
```json
{"instruction": "...", "input": "...", "output": "..."}
```

## Scalability Considerations

### Processing 1143 Documents x N Questions Each

**Estimate:** 1143 docs x 4 questions avg = ~4,572 QA pairs

| Stage | API Calls | Estimated Time | Cost Estimate |
|-------|-----------|----------------|---------------|
| Question Gen | ~1143 | ~19 min (at 1/sec) | Low (input only) |
| Answer Gen | ~4572 | ~76 min (at 1/sec) | Medium |
| Validation | ~4572 | ~76 min (at 1/sec) | Medium |
| **Total** | **~10,287** | **~3 hours** | **Medium** |

### Rate Limiting Strategy

Reuse existing pattern from src/ai/gemini.py:

```python
def batch_generate_qa(
    items: list[tuple[Document, Persona]],
    max_workers: int = 10,  # Parallel threads
    delay: float = 0.1      # Delay between calls
) -> list[QAPair]:
```

**Key optimizations:**
- Batch size of 50 (existing pattern)
- ThreadPoolExecutor with 10 workers
- 100ms delay between API calls
- Exponential backoff on rate limit errors

### Checkpointing

For long-running processes, save progress:

```python
# Save checkpoint after each batch
checkpoint = {
    "processed_documents": [...],
    "generated_pairs": [...],
    "last_batch": 42,
    "timestamp": "2026-01-24T10:30:00Z"
}
save_checkpoint(checkpoint, "qa_pairs/.checkpoint.json")

# Resume from checkpoint on restart
checkpoint = load_checkpoint("qa_pairs/.checkpoint.json")
start_batch = checkpoint["last_batch"] + 1
```

## Patterns to Follow

### From Existing Codebase

1. **Pydantic for structured output** (src/ai/gemini.py)
   ```python
   class GeneratedQuestion(BaseModel):
       text: str
       type: str
       confidence: float
   ```

2. **ThreadPoolExecutor for batching** (src/ai/gemini.py)
   ```python
   with ThreadPoolExecutor(max_workers=10) as executor:
       results = list(executor.map(process_single, items))
   ```

3. **CLI pattern** (generate_prompts.py)
   ```python
   parser.add_argument('--input', '-i', type=Path, default=Path('./converted'))
   parser.add_argument('--output', '-o', type=Path, default=Path('./qa_pairs'))
   parser.add_argument('--batch-size', type=int, default=50)
   ```

4. **Graceful degradation** (src/ai/gemini.py)
   ```python
   if not api_key:
       logger.warning("GEMINI_API_KEY not set")
       return None
   ```

### From Industry Best Practices

5. **RAGAS-style quality scoring** for validation
6. **JSONL format** for streaming and parallel processing
7. **Source grounding** with explicit citations
8. **Persona-based generation** for diverse, realistic questions

## Anti-Patterns to Avoid

1. **Single-pass generation without validation**
   - Always validate generated content against sources
   - Hallucinations are common in synthetic data

2. **Ignoring document metadata**
   - Use frontmatter (category, subcategory, keywords) for persona selection
   - Better targeting = higher quality questions

3. **Overloading API with synchronous calls**
   - Use batching and parallelization
   - Respect rate limits with delays and backoff

4. **Monolithic output format**
   - Support multiple export formats for different use cases
   - Keep raw data separate from formatted exports

5. **No checkpointing for long processes**
   - Save progress regularly
   - Enable resume from failure

## Sources

- [OpenAI Cookbook: How to Handle Rate Limits](https://cookbook.openai.com/examples/how_to_handle_rate_limits)
- [Claude Docs: Batch Processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)
- [Ragas: All About Synthetic Data Generation](https://blog.ragas.io/all-about-synthetic-data-generation)
- [YData: Synthetic Q&A and Document Generation](https://ydata.ai/resources/synthetic-qa-documents)
- [Persona-SQ: Personalized Suggested Question Generation](https://arxiv.org/html/2412.12445v1)
- [GitHub: synthetic-LLM-QA-dataset-generator](https://github.com/nalinrajendran/synthetic-LLM-QA-dataset-generator)
- [Multi-Modal RAG with Visual Answer Grounding](https://medium.com/data-science-collective/multi-modal-rag-with-visual-answer-grounding-e8875a486c88)
- Existing codebase patterns: src/ai/gemini.py, generate_prompts.py, pipeline.py

# Research Summary: v5.0 QA Generation Pipeline

**Project:** BoBot-Scrape v5.0
**Domain:** Synthetic QA generation for Swedish municipal care worker documents
**Researched:** 2026-01-24
**Confidence:** HIGH

## Executive Summary

The v5.0 QA generation pipeline can be built entirely on the existing stack with only numpy as a new dependency. Gemini handles all LLM tasks: question generation, answer generation, validation scoring, and embeddings. The ~1100 converted markdown documents fit comfortably in memory for semantic search using numpy cosine similarity, eliminating the need for vector databases. The existing codebase patterns (Pydantic structured output, ThreadPoolExecutor batching, graceful degradation) provide a solid foundation.

The recommended approach is a four-stage pipeline: (1) persona-driven question generation from documents, (2) grounded answer generation with source citations, (3) two-stage validation (source verification + quality scoring), and (4) JSONL export. Questions should be generated from realistic care worker personas (roll + erfarenhet + situation + sprakbakgrund), and answers must use plain Swedish (klarsprak) accessible to second-language speakers.

The critical risks are hallucinated procedure steps and second-language accessibility. Hallucination prevention requires strict grounding: extraction-style prompts, source snippets embedded in outputs, and validation that compares answer tokens to source documents. For accessibility, target CEFR B1 reading level with short sentences, active voice, and common vocabulary. Budget $10-15 for API costs to generate ~5000 QA pairs.

## Stack Decision

**Core:** Stay on existing stack (google-genai, Pydantic, python-dotenv). Already proven for Swedish text and structured output.

**New dependency:** numpy only. For cosine similarity in semantic search. No vector database needed at this scale.

**Not needed:** LangChain (unnecessary abstraction), ChromaDB/Faiss (overkill for 1100 docs), RAGAS (designed for evaluation, not generation), multiple LLM providers (stick with Gemini for consistency).

**Models:**
- gemini-3-flash-preview: Question generation, answer generation, validation (fast, cheap)
- gemini-embedding-001: Document embeddings for retrieval (768 dimensions, native Google)

## Key Features

**Table Stakes (must have):**
- Document grounding with explicit source citations
- Groundedness verification (LLM-as-judge)
- Question diversity via type tags (faktafragor, procedurfragor, situationsfragor, gransningsfragor, undantagsfragor)
- Batch processing with parallelization
- JSONL output format for HuggingFace compatibility
- Source attribution linking each QA pair to document

**Differentiators:**
- Persona-driven questions (roll + erfarenhet + situation + sprakbakgrund)
- Plain Swedish (klarsprak) for second-language speakers
- Mobile-first answer length (2-3 sentences facts, 10 steps max procedures)
- Stress-appropriate formatting for urgent situations
- Verksamhet-aware context using existing metadata

**Defer to v6+:**
- Cross-document synthesis (high complexity)
- Full RAGAS evaluation suite (simpler checks sufficient for now)
- Manual review workflow (start with automated filters)

## Architecture Pattern

**High-level flow:**
```
converted/*.md --> Question Generator --> Answer Generator --> Validator --> Exporter --> qa_pairs.jsonl
     |                    |                     |                |
     |               Persona Engine       Document Retriever  Source Verifier
     |                                          |                |
     +------------------------------------------+----------------+
                      Document context flows back for grounding
```

**Major components:**
1. **generate_qa.py** - CLI orchestrator, follows existing generate_prompts.py pattern
2. **src/qa/persona.py** - Persona model (role, situation, question styles) and selection logic
3. **src/qa/question_generator.py** - Generate 3-5 questions per document using personas
4. **src/qa/answer_generator.py** - Generate grounded answers with citations
5. **src/qa/validator.py** - Two-stage: source verification + quality assessment
6. **src/qa/exporter.py** - JSONL export with metadata

**Key pattern:** Reuse Gemini Pydantic structured output from src/ai/gemini.py. Reuse ThreadPoolExecutor batching with rate limiting.

## Critical Pitfalls

1. **Hallucinated Procedure Steps** (P1) - LLM invents phone numbers, contacts, or steps not in source. Prevention: extraction-style prompts ("What does the document say about X?"), require explicit source quotes, post-generation token comparison.

2. **Second-Language Accessibility** (L2) - Complex Swedish alienates target users. Prevention: include klarsprak guidelines in prompts, target CEFR B1, measure LIX readability score, prefer active voice and short sentences.

3. **Role/Responsibility Confusion** (D2) - QA mixes up who does what. Prevention: require explicit role specification in questions, generate role-specific QA pairs, validate against role-specific document content.

4. **LLM-as-Judge Bias** (V1) - Same model family generates and validates, creating blind spots. Prevention: use two-stage validation (structural source verification + semantic quality), include 5-10% human review sample, weight validation toward source-grounding not plausibility.

5. **Missing Critical Safety Information** (P4) - Routine content overrepresented, safety procedures underrepresented. Prevention: tag documents by safety-criticality, require minimum QA pairs for safety categories, manual review sample from high-stakes documents.

## Build Order Recommendation

### Phase 1: Core Infrastructure
**Rationale:** Foundation for all other phases. Minimal dependencies.
**Delivers:** Persona model, module structure, CLI scaffold
**Duration:** 1-2 days
**Components:**
- src/qa/__init__.py
- src/qa/persona.py (Pydantic model + YAML loader)
- configs/personas.yaml (5-7 starter personas)
- generate_qa.py CLI scaffold (--input, --output, --batch-size)

### Phase 2: Question Generation
**Rationale:** Depends on personas. Enables testing before answer generation.
**Delivers:** Questions from documents using persona-driven prompts
**Duration:** 2-3 days
**Avoids:** P3 (overly specific questions) via persona variety
**Components:**
- src/qa/question_generator.py
- Pydantic model: GeneratedQuestion
- Prompt templates for different question types

### Phase 3: Answer Generation
**Rationale:** Depends on questions. Includes retrieval for grounding.
**Delivers:** Grounded answers with source citations
**Duration:** 2-3 days
**Avoids:** P1 (hallucination) via extraction-style prompts
**Components:**
- src/qa/answer_generator.py
- src/qa/embeddings.py (numpy cosine similarity)
- Pydantic model: GeneratedAnswer
- Citation format: [source:filename.md#section]

### Phase 4: Validation
**Rationale:** Depends on answers. Quality gate before export.
**Delivers:** Two-stage validation with quality scores
**Duration:** 2-3 days
**Avoids:** V1 (LLM bias) via separate validation prompts, V3 (shallow validation) via semantic checking
**Components:**
- src/qa/validator.py
- Pydantic model: ValidationResult
- Source verification prompts
- Quality assessment prompts

### Phase 5: Export and Integration
**Rationale:** Final phase. Complete pipeline integration.
**Delivers:** JSONL export, pipeline.py integration
**Duration:** 1-2 days
**Components:**
- src/qa/exporter.py
- Update pipeline.py with --generate-qa flag
- qa_pairs/ directory structure

### Phase 6: Scale Testing
**Rationale:** Full corpus run after pipeline complete.
**Delivers:** ~5000 validated QA pairs, tuned parameters
**Duration:** 1-2 days (wall clock includes API time)
**Components:**
- Checkpointing for long runs
- Quality review and persona refinement
- Coverage report by category

## Open Questions

**Needs domain expert input:**
1. **Persona validation** - Are the 5-7 starter personas realistic for care workers? Need input from actual underskoterska or enhetschef.
2. **Safety-critical document tagging** - Which document categories should be flagged for mandatory QA coverage? (e.g., Hot och vald, Fallprevention)
3. **Terminology mapping** - What are the canonical terms for common concepts? (e.g., KIA-anmalan vs tillbudsrapport vs avvikelseanmalan)
4. **Quality threshold calibration** - What validation score constitutes acceptable quality for production use?

**Can resolve during implementation:**
- Optimal batch size (start with 50, tune based on rate limits)
- Number of questions per document (start with 3-5, tune based on document length)
- Chunk size for embedding (start with 500-800 tokens)

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified with official Gemini docs, already proven in codebase |
| Features | MEDIUM-HIGH | Based on NVIDIA/AWS best practices, adapted for Swedish municipal domain |
| Architecture | HIGH | Builds on existing patterns, follows industry synthetic data generation flow |
| Pitfalls | MEDIUM | WebSearch-verified, some domain-specific reasoning |

**Overall confidence:** HIGH

### Gaps to Address

- **Gold standard QA set** - Need 50-100 human-annotated QA pairs for validation baseline. Consider creating during Phase 4.
- **Swedish readability measurement** - LIX score calculation not built-in. May need simple implementation or sampling.
- **Document staleness detection** - Design for v5.0, implement in maintenance phase.

## Sources

### High Confidence (Official Documentation)
- Gemini API Structured Output: https://ai.google.dev/gemini-api/docs/structured-output
- Gemini Embeddings: https://ai.google.dev/gemini-api/docs/embeddings
- HuggingFace Datasets Loading: https://huggingface.co/docs/datasets
- Existing codebase patterns: src/ai/gemini.py, generate_prompts.py, pipeline.py

### Medium Confidence (Industry Best Practices)
- NVIDIA SDG Pipeline: https://developer.nvidia.com/blog/evaluating-and-enhancing-rag-pipeline-performance-using-synthetic-data/
- AWS Synthetic Data for RAG: https://aws.amazon.com/blogs/machine-learning/generate-synthetic-data-for-evaluating-rag-systems/
- Persona Hub Research: https://arxiv.org/abs/2406.20094
- RAGAS Documentation: https://docs.ragas.io/en/stable/
- CDC Plain Language: https://www.cdc.gov/health-literacy/php/develop-materials/plain-language.html

### Domain-Specific
- Swedish Medical LLM Benchmark: https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full
- Plain Swedish Language (Klarsprak): https://www.isof.se/other-languages/english/plain-swedish-language

---
*Research completed: 2026-01-24*
*Ready for roadmap: yes*

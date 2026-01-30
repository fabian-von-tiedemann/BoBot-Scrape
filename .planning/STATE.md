# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-24)

**Core value:** Generera tusentals validerade QA-par fran kunskapsbasen for AI-assistenttraning
**Current focus:** v5.0 QA Generation Pipeline - Phase 30 In Progress

## Current Position

Phase: 30 of 31 (Validation Pipeline)
Plan: 01 of 02 complete
Status: Phase 30 in progress
Last activity: 2026-01-30 - Completed 30-01-PLAN.md

Progress: [=======...] 70% (4 of 5 phases)

## Performance Metrics

**Velocity:**

- Total plans completed: 30 (v1.0-v4.0 + v5.0)
- Average duration: ~5 min
- Total execution time: ~167 min

**By Milestone:**

| Milestone           | Phases | Plans | Total Time |
|---------------------|--------|-------|------------|
| v1.0 MVP            | 1-4    | 5     | ~49 min    |
| v2.0 Doc Processing | 5-8    | 4     | ~21 min    |
| v2.1 Improvements   | 9-10   | 2     | ~5 min     |
| v2.2 Frontmatter    | 11-14  | 5     | ~10 min    |
| v2.3 Schema Upgrade | 15-17  | 1     | ~3 min     |
| v2.4 KB Delivery    | 18     | 1     | ~3 min     |
| v2.5 System Prompt  | 19-21  | 3     | ~12 min    |
| v3.0 Digi Commands  | 22     | 1     | ~3 min     |
| v3.1 Improvements   | 23     | 1     | ~3 min     |
| v4.0 Pipeline Ref   | 24-26  | 3     | ~34 min    |
| v5.0 QA Pipeline    | 27-31  | 5     | ~30 min    |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.

**v5.0 Phase 27 Decisions:**
- Persona ID format: {roll}-{erfarenhet}-{sprakbakgrund}
- Pydantic Literal types for constrained field validation
- CLI follows existing generate_prompts.py patterns

**v5.0 Phase 28 Decisions:**

- Model: gemini-2.0-flash (gemini-3-flash-preview not available)
- Persona selection heuristics: nyanstald for intro docs, natt persona for night shift docs
- Deduplication threshold: 0.85 similarity ratio
- Rate limiting: max_workers=5, delay=0.2s

**v5.0 Phase 29 Decisions (Plan 01):**

- Embedding model: KBLab/sentence-bert-swedish-cased (0.918 Pearson on SweParaphrase)
- Chunk size: 512 tokens with 128 overlap (Microsoft RAG guidelines)
- Vector search: FAISS IndexFlatIP with L2 normalization (cosine similarity)
- Token counting: tiktoken cl100k_base encoding

**v5.0 Phase 29 Decisions (Plan 02):**

- Extraction-style prompting: prefer direct quotes over paraphrasing for accuracy
- Citation format: [source:document.md#section] inline immediately after content
- Klarsprak enforcement: max 15 words per sentence, active voice, du-tilltal
- Coverage tracking: full/partial/none with confidence score 0.0-1.0

**v5.0 Phase 30 Decisions (Plan 01):**

- Similarity thresholds: >=0.75 auto-pass, 0.5-0.75 LLM borderline check, <0.5 auto-fail
- Composite weights: source 0.3, relevans 0.2, korrekthet 0.3, fullstandighet 0.2
- Early exit: Skip quality assessment if source verification fails to save API calls
- Claim extraction: Split answer by sentences, filter trivial (<10 chars)

### Deferred Issues

None.

### Pending Todos

2 todos from v4.0 - `/gsd:check-todos` to review

### Blockers/Concerns

None.

### Roadmap Evolution

- v1.0-v4.0: 26 phases shipped (see PROJECT.md)
- v5.0 QA Generation Pipeline: Phases 27-31 (current)
  - Phase 27: Core Infrastructure - COMPLETE
  - Phase 28: Question Generation - COMPLETE
  - Phase 29: Answer Generation - COMPLETE (retrieval + generation)
  - Phase 30: QA Validation - Plan 01 complete (validation core)

## Session Continuity

Last session: 2026-01-30
Stopped at: Phase 30-01 complete, ready for 30-02 CLI
Resume file: None

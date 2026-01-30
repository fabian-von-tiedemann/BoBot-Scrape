# Roadmap: BoBot-Scrape v5.0 QA Generation Pipeline

## Overview

This milestone builds a complete QA generation pipeline that transforms the existing knowledge base (1,086 converted markdown documents) into thousands of validated question-answer pairs for AI assistant training. The pipeline progresses through persona modeling, question generation, answer grounding, validation, and export - each phase delivering a complete, testable capability that feeds the next.

## Milestones

- v1.0-v4.0: See PROJECT.md Validated Requirements (shipped)
- **v5.0 QA Generation Pipeline** - Phases 27-31 (current)

## Phases

- [x] **Phase 27: Core Infrastructure** - Persona model and module scaffold
- [x] **Phase 28: Question Generation** - Generate persona-driven questions from documents
- [x] **Phase 29: Answer Generation** - Ground answers in source documents with citations
- [x] **Phase 30: Validation Pipeline** - Two-stage quality gate (source + quality)
- [ ] **Phase 31: Export & Integration** - JSONL export and pipeline integration

## Phase Details

### Phase 27: Core Infrastructure
**Goal**: Establish persona model and QA module structure as foundation for generation pipeline
**Depends on**: v4.0 complete (converted documents exist in KB)
**Requirements**: PERS-01, PERS-02, PERS-03
**Success Criteria** (what must be TRUE):
  1. Persona model exists as Pydantic class with roll, erfarenhet, situation, sprakbakgrund fields
  2. YAML config file contains 5-10 realistic care worker personas
  3. CLI scaffold (generate_qa.py) accepts --input, --output, --personas arguments
  4. src/qa/ module structure exists with __init__.py and persona.py
**Plans**: 1 plan

Plans:
- [x] 27-01-PLAN.md - Create persona model, YAML config, and CLI scaffold

### Phase 28: Question Generation
**Goal**: Generate 3-5 diverse questions per document using persona-driven prompts
**Depends on**: Phase 27 (persona model required)
**Requirements**: QGEN-01, QGEN-02, QGEN-03, QGEN-04, QGEN-05
**Success Criteria** (what must be TRUE):
  1. Running generator on a document produces 3-5 questions in Swedish
  2. Each question is formulated from a specific persona's perspective
  3. Each question includes reference to its source document (filename, section)
  4. Batch mode processes multiple documents with progress bar
  5. Questions saved to intermediate output file for inspection
**Plans**: 1 plan

Plans:
- [x] 28-01-PLAN.md - Question generation with Pydantic models, Gemini integration, batch processing

### Phase 29: Answer Generation
**Goal**: Generate grounded answers with explicit source citations in plain Swedish
**Depends on**: Phase 28 (questions required)
**Requirements**: AGEN-01, AGEN-02, AGEN-03, AGEN-04
**Success Criteria** (what must be TRUE):
  1. Each answer is directly grounded in the source document content
  2. Answers include citation format [source:filename.md#section]
  3. Answer text uses klarsprak (B1 Swedish, short sentences, active voice)
  4. Extraction-style generation (quotes relevant text rather than paraphrasing)
**Plans**: 2 plans

Plans:
- [x] 29-01-PLAN.md - Semantic retrieval infrastructure (chunking, Swedish embeddings, FAISS index)
- [x] 29-02-PLAN.md - Answer generation with citations and CLI integration

### Phase 30: Validation Pipeline
**Goal**: Two-stage validation filtering out hallucinations and low-quality pairs
**Depends on**: Phase 29 (QA pairs required)
**Requirements**: VALD-01, VALD-02, VALD-03, VALD-04, VALD-05
**Success Criteria** (what must be TRUE):
  1. Source verification confirms answer content exists in referenced document
  2. Quality assessment scores relevans, korrekthet, fullstandighet
  3. Each QA pair has validation_score in output
  4. Pipeline filters out pairs below quality threshold
  5. Separate output streams for passed vs failed validation
**Plans**: 2 plans

Plans:
- [x] 30-01-PLAN.md - Validation module core (Pydantic models, source verification, quality assessment)
- [x] 30-02-PLAN.md - CLI integration and batch processing with JSONL output

### Phase 31: Export & Integration
**Goal**: Complete pipeline with JSONL export and integration into main workflow
**Depends on**: Phase 30 (validated QA pairs required)
**Requirements**: EXPRT-01, EXPRT-02, EXPRT-03, INTG-01, INTG-02, INTG-03
**Success Criteria** (what must be TRUE):
  1. JSONL export works with HuggingFace datasets format
  2. Each QA pair includes metadata: persona, source, validation_score
  3. Separate files for passed (qa_pairs.jsonl) and failed (qa_rejected.jsonl) pairs
  4. generate_qa.py works as standalone CLI
  5. pipeline.py accepts --generate-qa flag to include QA generation
  6. Checkpointing allows resume after interruption
**Plans**: TBD

Plans:
- [ ] 31-01: [To be planned]

## Progress

**Execution Order:** Phase 27 -> 28 -> 29 -> 30 -> 31

| Phase | Goal | Plans Complete | Status | Completed |
|-------|------|----------------|--------|-----------|
| 27. Core Infrastructure | Persona model & scaffold | 1/1 | ✓ Complete | 2026-01-25 |
| 28. Question Generation | Persona-driven questions | 1/1 | ✓ Complete | 2026-01-26 |
| 29. Answer Generation | Grounded answers | 2/2 | ✓ Complete | 2026-01-29 |
| 30. Validation Pipeline | Two-stage quality gate | 2/2 | ✓ Complete | 2026-01-30 |
| 31. Export & Integration | JSONL & pipeline | 0/TBD | Not started | - |

---
*Roadmap created: 2026-01-24*
*Milestone: v5.0 QA Generation Pipeline*

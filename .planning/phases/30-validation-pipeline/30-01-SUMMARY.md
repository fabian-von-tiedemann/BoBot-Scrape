---
phase: 30-validation-pipeline
plan: 01
subsystem: qa-pipeline
tags: [validation, pydantic, llm-as-judge, semantic-similarity, gemini]

# Dependency graph
requires:
  - phase: 29-answer-generation
    provides: "SwedishRetriever, GeneratedAnswer, QAEntry models"
provides:
  - "SourceVerification model for source grounding checks"
  - "QualityAssessment model for LLM-as-judge scoring"
  - "ValidationResult model for combined pass/fail"
  - "verify_source() with semantic similarity + LLM borderline"
  - "assess_quality() with three-dimension scoring"
  - "validate_qa_pair() orchestrating two-stage pipeline"
affects: [30-02, 31-export, qa-pipeline-cli]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-stage validation (source first, quality second)"
    - "LLM borderline verification for ambiguous similarity"
    - "Weighted composite scoring with korrekthet priority"

key-files:
  created:
    - src/qa/validator.py
  modified:
    - src/qa/__init__.py

key-decisions:
  - "Semantic similarity thresholds: >=0.75 auto-pass, 0.5-0.75 LLM check, <0.5 auto-fail"
  - "Default weights: source 0.3, relevans 0.2, korrekthet 0.3, fullstandighet 0.2"
  - "Early exit if source verification fails to save LLM calls"

patterns-established:
  - "Extract claims from answer text for granular verification"
  - "Swedish LLM-as-judge prompt with explicit scoring rubric"
  - "Composite score with configurable weights"

# Metrics
duration: 4min
completed: 2026-01-30
---

# Phase 30 Plan 01: Validation Pipeline Core Summary

**Two-stage QA validation with semantic similarity source verification and LLM-as-judge quality assessment (relevans, korrekthet, fullstandighet)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-01-30T07:32:14Z
- **Completed:** 2026-01-30T07:35:58Z
- **Tasks:** 3/3
- **Files modified:** 2

## Accomplishments

- Created Pydantic models for SourceVerification, QualityAssessment, and ValidationResult
- Implemented verify_source() with claim extraction and semantic similarity scoring
- Added LLM borderline verification for 0.5-0.75 similarity range using Gemini
- Implemented assess_quality() with Swedish LLM-as-judge prompt
- Created compute_composite_score() with configurable weights prioritizing korrekthet
- Built validate_qa_pair() orchestrating full two-stage pipeline
- Exported all components from src/qa/__init__.py

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Pydantic models for validation results** - `2c2c3c5` (feat)
2. **Task 2: Implement source verification with semantic similarity** - `026db21` (feat)
3. **Task 3: Implement quality assessment and composite scoring** - `d14ae05` (feat)

## Files Created/Modified

- `src/qa/validator.py` - Two-stage validation pipeline core (506 lines)
- `src/qa/__init__.py` - Added validator exports

## Decisions Made

1. **Similarity thresholds:** Used 0.75 for auto-pass, 0.5-0.75 for borderline LLM check, <0.5 for auto-fail per RESEARCH.md recommendations
2. **Composite weights:** Prioritized korrekthet at 0.3 (accuracy critical for training data), with source at 0.3, relevans and fullstandighet at 0.2 each
3. **Early exit:** If source verification fails (<0.5 similarity and not grounded), skip quality assessment to save LLM API calls
4. **Claim extraction:** Split answer by sentences, filter trivial (<10 chars) and reference sentences

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed successfully without blockers.

## User Setup Required

None - no external service configuration required. Uses existing GEMINI_API_KEY environment variable from previous phases.

## Next Phase Readiness

- Validation core complete, ready for Plan 02 (CLI and batch processing)
- SwedishRetriever and doc_contents loading patterns established in RESEARCH.md
- ValidationResult.model_dump() ready for JSONL output

---
*Phase: 30-validation-pipeline*
*Completed: 2026-01-30*

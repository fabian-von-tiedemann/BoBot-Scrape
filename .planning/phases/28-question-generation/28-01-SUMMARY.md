---
phase: 28-question-generation
plan: 01
subsystem: qa
tags: [pydantic, gemini, yaml, batch-processing, persona, question-generation]

# Dependency graph
requires: [27-core-infrastructure]
provides:
  - GeneratedQuestion Pydantic model for Gemini structured output
  - QuestionBatch model with 3-5 question constraint
  - QuestionEntry model for YAML output with full metadata
  - Batch processing with Rich progress bars
  - Deduplication with difflib similarity matching
  - YAML output grouped by category
affects: [29-answer-generation, 30-validation, 31-export]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Gemini structured output with Pydantic response_schema
    - ThreadPoolExecutor batch processing with rate limiting
    - Rich progress bars for CLI feedback
    - difflib.SequenceMatcher for text similarity deduplication

key-files:
  created:
    - qa/questions.yaml
  modified:
    - src/qa/question.py
    - src/qa/__init__.py
    - generate_qa.py

key-decisions:
  - "Model: gemini-2.0-flash (gemini-3-flash-preview not available)"
  - "Persona selection heuristics: nyanstald for intro docs, natt persona for night shift docs, random for variety"
  - "Deduplication threshold: 0.85 similarity ratio"
  - "Rate limiting: max_workers=5, delay=0.2s between calls"

patterns-established:
  - "Question generation with persona-driven prompts"
  - "YAML output format for human-readable QA data"
  - "CLI single-file mode for testing, batch mode for production"

# Metrics
duration: 3min
completed: 2026-01-26
---

# Phase 28 Plan 01: Question Generation Summary

**Persona-driven question generation from documents using Gemini API with batch processing, deduplication, and YAML output**

## Performance

- **Duration:** 3 min
- **Started:** 2026-01-26T12:13:04Z
- **Completed:** 2026-01-26T12:17:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- GeneratedQuestion, QuestionBatch, QuestionEntry Pydantic models for structured LLM output
- QUESTION_GENERATION_PROMPT template for persona-driven Swedish questions
- select_persona_for_document() with heuristics for best-fit persona matching
- generate_questions_for_document() with Gemini API call and rate limiting
- process_documents_batch() with ThreadPoolExecutor and Rich progress bars
- deduplicate_questions() with difflib.SequenceMatcher (0.85 threshold)
- write_questions_yaml() with category grouping
- CLI single-file mode for testing individual documents
- CLI batch mode with --limit option for controlled processing

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Pydantic models and prompt** - `218fffe` (feat)
2. **Task 2: Generation functions** - Combined with Task 1 (natural code organization)
3. **Task 3: Wire CLI** - `158ecd7` (feat)

## Files Created/Modified

- `src/qa/question.py` - Question models and generation logic (new)
- `src/qa/__init__.py` - Added question module exports
- `generate_qa.py` - Full CLI implementation with single-file and batch modes
- `qa/questions.yaml` - Generated output file with questions grouped by category

## Decisions Made

- Used `gemini-2.0-flash` model instead of `gemini-3-flash-preview` (404 error on original model)
- Combined Tasks 1 and 2 into single file (question.py) for better code organization
- Added dotenv loading to CLI for GEMINI_API_KEY from .env file
- Question types: factual, procedural, situational, clarification (as specified)
- Persona matching heuristics: intro/checklist docs -> nyanstald, night shift docs -> natt persona

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Changed Gemini model name**
- **Found during:** Task 3
- **Issue:** Model `gemini-3-flash-preview` from research doc returned 404 NOT_FOUND
- **Fix:** Changed to `gemini-2.0-flash` which is currently available
- **Files modified:** src/qa/question.py

**2. [Rule 2 - Missing Critical] Added dotenv loading to CLI**
- **Found during:** Task 3
- **Issue:** CLI didn't load .env file, requiring manual GEMINI_API_KEY export
- **Fix:** Added `from dotenv import load_dotenv` and load_dotenv() call
- **Files modified:** generate_qa.py

## Issues Encountered

None - all issues were auto-fixed per deviation rules.

## Requirements Verification

- QGEN-01: Generera fragor fran dokumentinnehall med Gemini - VERIFIED (questions.yaml has questions)
- QGEN-02: Persona-drivna fragor - VERIFIED (persona field in each question with full details)
- QGEN-03: Kalldokumentreferens - VERIFIED (source_document and section fields present)
- QGEN-04: 3-5 fragor per dokument - VERIFIED (QuestionBatch enforces min_length=3, max_length=5)
- QGEN-05: Batch-generering med progress - VERIFIED (Rich progress bar shown during batch processing)

## User Setup Required

- GEMINI_API_KEY must be set in .env file (already present in project)

## Next Phase Readiness

- Question generation infrastructure complete for Phase 29 (Answer Generation)
- qa/questions.yaml provides input for answer generation
- All exports verified working from src.qa module
- Ready to add answer generation logic in Phase 29

---
*Phase: 28-question-generation*
*Completed: 2026-01-26*

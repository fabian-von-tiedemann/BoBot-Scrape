---
phase: 20-system-prompt-generator
plan: 01
subsystem: ai
tags: [gemini, pydantic, system-prompt, cli, argparse]

# Dependency graph
requires:
  - phase: 19-frontmatter-indexer
    provides: Index files per verksamhet with document metadata
provides:
  - SystemPrompt Pydantic model for structured prompts
  - generate_system_prompt() Gemini-powered generation
  - generate_prompts.py CLI for batch processing
  - 15 verksamhet-specific system prompt files
affects: [21-general-prompt-template]

# Tech tracking
tech-stack:
  added: []
  patterns: [gemini-structured-output, cli-batch-processing]

key-files:
  created: [src/prompt_generator.py, generate_prompts.py, prompts/*-PROMPT.md]
  modified: []

key-decisions:
  - "Used same Gemini pattern as src/ai/gemini.py for consistency"
  - "Structured output via Pydantic model for predictable prompt format"

patterns-established:
  - "Verksamhet-specific prompts with intro/areas/types/guidance structure"

issues-created: []

# Metrics
duration: 5min
completed: 2026-01-14
---

# Phase 20-01: System Prompt Generator Summary

**Gemini-powered system prompt generator producing 15 verksamhet-specific AI assistant prompts from index documents**

## Performance

- **Duration:** 5 min
- **Started:** 2026-01-14T16:36:12Z
- **Completed:** 2026-01-14T16:41:39Z
- **Tasks:** 2
- **Files modified:** 16 (1 module, 1 CLI, 15 prompts)

## Accomplishments

- Created `src/prompt_generator.py` with SystemPrompt Pydantic model and Gemini integration
- Created `generate_prompts.py` CLI for batch prompt generation
- Generated 15 verksamhet-specific system prompts in `prompts/` directory
- Each prompt contains Swedish introduction, key areas, document types summary, and AI guidance

## Task Commits

Each task was committed atomically:

1. **Task 1: Create prompt generator module** - `c4c474b` (feat)
2. **Task 2: Create prompt generator CLI** - `bf2c61e` (feat)

**Plan metadata:** (this commit) (docs: complete plan)

## Files Created/Modified

- `src/prompt_generator.py` - SystemPrompt model, generate_system_prompt(), format_prompt()
- `generate_prompts.py` - CLI with --input, --output, --verbose arguments
- `prompts/Hemtjänst-PROMPT.md` - Example: 7 key areas, Swedish content
- `prompts/*.md` - 15 total prompt files for all verksamheter

## Decisions Made

- Used same Gemini pattern as `src/ai/gemini.py` (Client, structured output via Pydantic)
- Prompt structure: Introduction → Key Areas → Document Types → Guidance
- All content in Swedish as per requirements

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing google-genai to correct Python**
- **Found during:** Task 2 (CLI execution)
- **Issue:** google-genai not installed for Python 3.13 (pip3 installed to Python 3.9)
- **Fix:** Ran `/usr/local/bin/python3 -m pip install google-genai`
- **Files modified:** None (dependency installation only)
- **Verification:** All 15 prompts generated successfully
- **Committed in:** bf2c61e (part of Task 2 commit)

---

**Total deviations:** 1 auto-fixed (blocking), 0 deferred
**Impact on plan:** Dependency issue resolved, no scope creep.

## Issues Encountered

None - plan executed successfully after dependency fix.

## Next Phase Readiness

- 15 verksamhet-specific system prompts ready in `prompts/`
- Ready for Phase 21: General Prompt Template (combine general + specific parts)

---
*Phase: 20-system-prompt-generator*
*Completed: 2026-01-14*

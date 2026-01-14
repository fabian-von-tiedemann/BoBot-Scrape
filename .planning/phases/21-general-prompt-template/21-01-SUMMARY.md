---
phase: 21-general-prompt-template
plan: 01
subsystem: prompts
tags: [system-prompt, prompt-engineering, cli, python]

# Dependency graph
requires:
  - phase: 20-system-prompt-generator
    provides: 15 verksamhet-specific prompts in prompts/*-PROMPT.md
provides:
  - General system prompt template (GENERAL.md)
  - Prompt combiner module (src/prompt_combiner.py)
  - Combiner CLI (combine_prompts.py)
  - 15 combined final prompts (prompts/combined/)
affects: [ai-assistant, deployment]

# Tech tracking
tech-stack:
  added: []
  patterns: [prompt-combination, cli-pattern]

key-files:
  created: [prompts/GENERAL.md, src/prompt_combiner.py, combine_prompts.py, prompts/combined/*-COMBINED.md]
  modified: []

key-decisions:
  - "General prompt in Swedish with 6 sections: Identitet, Uppgift, Tonalitet, Principer, Språk, Format"
  - "Combined prompts use --- separator between general and specific content"
  - "Output filename pattern: {verksamhet}-COMBINED.md"

patterns-established:
  - "Prompt combination: general foundation + verksamhet-specific guidance"

issues-created: []

# Metrics
duration: 2min
completed: 2026-01-14
---

# Phase 21 Plan 01: General Prompt Template Summary

**General Swedish system prompt template with 6 sections + prompt combiner generating 15 combined final prompts for AI assistant deployment**

## Performance

- **Duration:** 2 min
- **Started:** 2026-01-14T19:00:39Z
- **Completed:** 2026-01-14T19:02:29Z
- **Tasks:** 2
- **Files modified:** 18 (3 source files + 15 combined prompts)

## Accomplishments

- Created general system prompt template (GENERAL.md) with 6 Swedish sections
- Built prompt combiner module with load/combine/write functions
- Generated 15 combined prompts in prompts/combined/
- Each combined prompt has general foundation followed by verksamhet-specific content

## Task Commits

Each task was committed atomically:

1. **Task 1: Create general system prompt template** - `254ff29` (feat)
2. **Task 2: Create prompt combiner module and CLI** - `d5b7c15` (feat)

**Plan metadata:** (this commit)

## Files Created/Modified

- `prompts/GENERAL.md` - General template with Identitet, Uppgift, Tonalitet, Principer, Språk, Format
- `src/prompt_combiner.py` - Module with load_general_prompt, load_specific_prompt, combine_prompts, write_combined
- `combine_prompts.py` - CLI with --general, --input, --output arguments
- `prompts/combined/` - 15 combined prompts:
  - Bemanningsenheten-COMBINED.md
  - Boendestöd-COMBINED.md
  - Dagverksamhet-COMBINED.md
  - Gruppbostad-COMBINED.md
  - Hemtjänst-COMBINED.md
  - Hälso- och sjukvård-COMBINED.md
  - Korttidsboende för äldre (SoL)-COMBINED.md
  - Korttidsvistelse för unga (LSS)-COMBINED.md
  - Kost-och måltidsenheten-COMBINED.md
  - Ledsagning, Avlösning och Kontaktperson-COMBINED.md
  - Mötesplatser-COMBINED.md
  - Personlig assistans-COMBINED.md
  - Serviceboende (LSS)-COMBINED.md
  - Servicehus (SoL)-COMBINED.md
  - Vård- och omsorgsboende-COMBINED.md

## Decisions Made

- General prompt written in Swedish with 6 standardized sections
- Combined prompts use `---` separator between general and specific content
- Filename pattern: `{verksamhet}-COMBINED.md` for easy identification

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Phase 21 complete (final phase of v2.5 milestone)
- **Milestone v2.5 System Prompt Generation COMPLETE**
- All 21 phases of the project finished
- 15 combined prompts ready for AI assistant deployment

---
*Phase: 21-general-prompt-template*
*Completed: 2026-01-14*

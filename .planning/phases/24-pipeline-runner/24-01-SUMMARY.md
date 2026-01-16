---
phase: 24-pipeline-runner
plan: 01
subsystem: pipeline
tags: [cli, subprocess, orchestration, etl]

# Dependency graph
requires:
  - phase: 23-parallel-ai
    provides: batch_generate_metadata for convert.py
provides:
  - Unified pipeline.py CLI that orchestrates all ETL stages
  - Timestamped run directories for versioned output
  - --skip-scrape, --skip-ai, --force flags for flexible execution
affects: [25-incremental-updates, 26-kb-sync]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "subprocess.run() with sys.executable for Python interpreter resolution"
    - "Timestamped output directories under runs/"

key-files:
  created:
    - pipeline.py
  modified: []

key-decisions:
  - "Use sys.executable instead of 'python' for subprocess calls"
  - "Run directory structure: runs/YYYY-MM-DD-HHMM/{downloads,converted,indexes,prompts}"

patterns-established:
  - "Pipeline stages execute sequentially with fail-fast behavior"
  - "Stage timing captured and displayed in summary"

# Metrics
duration: 8min
completed: 2026-01-16
---

# Phase 24 Plan 01: Pipeline Runner CLI Summary

**Unified pipeline.py CLI that orchestrates all 5 ETL stages (scrape, convert, index, generate, combine) with timestamped run directories**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-16T08:47:43Z
- **Completed:** 2026-01-16T08:56:11Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Created pipeline.py CLI with all required options (--run-dir, --skip-scrape, --skip-ai, --force)
- Implemented timestamped run directory structure (runs/YYYY-MM-DD-HHMM/)
- All 5 stages execute in sequence with correct path passing
- Verified pipeline completes successfully with --skip-scrape --skip-ai flags

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pipeline.py CLI** - `edb6f3b` (feat)
2. **Task 2: Test pipeline** - No commit (verification task, test passed)

## Files Created/Modified

- `pipeline.py` - Unified CLI that orchestrates all ETL stages with subprocess.run()

## Decisions Made

- Used sys.executable instead of hardcoded 'python' to ensure subprocess uses the same interpreter as the parent process
- General prompt sourced from root prompts/GENERAL.md (not run-specific) since it's shared across all runs

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed Python interpreter resolution**
- **Found during:** Task 2 (Pipeline test)
- **Issue:** subprocess.run() couldn't find 'python' in PATH
- **Fix:** Changed to use sys.executable for all subprocess calls
- **Files modified:** pipeline.py
- **Verification:** Pipeline test completed successfully
- **Committed in:** edb6f3b (amended into Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Fix essential for pipeline to function. No scope creep.

## Issues Encountered

- pyyaml module was missing from venv (installed with pip install pyyaml)
- 4 documents failed text extraction/markdown formatting (known issue, not related to pipeline)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Pipeline runner complete, ready for Phase 25 (Incremental Updates)
- Test run created in runs/test-run/ with 1143 markdown files, 15 indexes, 15 prompts, 15 combined prompts

---
*Phase: 24-pipeline-runner*
*Completed: 2026-01-16*

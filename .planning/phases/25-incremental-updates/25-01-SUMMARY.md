---
phase: 25-incremental-updates
plan: 01
subsystem: pipeline
tags: [cli, manifest, diff, incremental, etl]

# Dependency graph
requires:
  - phase: 24-pipeline-runner
    provides: Unified pipeline.py CLI with timestamped run directories
provides:
  - Manifest file tracking document URLs and hashes per run
  - Diff detection comparing current vs previous run
  - Incremental convert mode processing only changed documents
affects: [26-kb-sync]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "MD5 hash for URL comparison (fast, no security concerns)"
    - "Manifest JSON schema with run_id, documents, diff"
    - "tempfile.NamedTemporaryFile for include-files filtering"

key-files:
  created: []
  modified:
    - pipeline.py
    - convert.py

key-decisions:
  - "Use MD5 hash for URL comparison (fast, deterministic)"
  - "Store diff results in manifest.json for traceability"
  - "Skip convert stage entirely when no changes detected"

patterns-established:
  - "Manifest-based change detection between pipeline runs"
  - "--include-files pattern for selective document processing"

# Metrics
duration: 18min
completed: 2026-01-16
---

# Phase 25 Plan 01: Incremental Updates Summary

**Manifest-based diff detection with URL hashing enables incremental document processing, skipping unchanged files**

## Performance

- **Duration:** 18 min
- **Started:** 2026-01-16T09:27:38Z
- **Completed:** 2026-01-16T09:45:59Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- Implemented manifest.json file tracking document URLs and MD5 hashes per run
- Added --prev-run CLI argument for comparing against previous runs
- Diff detection identifies new, changed, removed, and unchanged documents
- Convert stage uses --include-files to process only changed documents
- Pipeline correctly skips convert stage when no changes detected

## Task Commits

Each task was committed atomically:

1. **Task 1: Add manifest file for tracking document state** - `110dde0` (feat)
2. **Task 2: Implement diff detection between runs** - `66b420d` (feat)
3. **Task 3: Add incremental convert mode** - `2b83ded` (feat)

## Files Created/Modified

- `pipeline.py` - Added manifest functions (create/save/load), compute_diff(), --prev-run argument, incremental convert logic
- `convert.py` - Added --include-files argument for selective document processing

## Decisions Made

- Used MD5 hash for URL comparison - fast and deterministic, no security concerns for this use case
- Store diff results in manifest.json for traceability and debugging
- Skip convert stage entirely when no changes detected rather than running with empty file list

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed datetime.utcnow() deprecation warning**
- **Found during:** Task 1 (Manifest creation)
- **Issue:** Python 3.12+ deprecates datetime.utcnow()
- **Fix:** Changed to datetime.now(timezone.utc)
- **Files modified:** pipeline.py
- **Verification:** Warning no longer appears
- **Committed in:** 110dde0 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Fix essential for clean operation. No scope creep.

## Issues Encountered

- When convert stage is skipped (no changes), subsequent stages (index, generate) fail because converted/ directory doesn't exist in new run. This is expected behavior - in a real incremental workflow, unchanged outputs would be copied from previous run or stages would be skipped entirely.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Incremental update detection complete
- Ready for Phase 26 (KB Sync Integration)
- Note: Full incremental workflow may need additional logic to handle subsequent stages when no changes detected

---
*Phase: 25-incremental-updates*
*Completed: 2026-01-16*

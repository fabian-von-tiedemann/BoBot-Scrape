# Phase 31: Export & Integration - Context

**Gathered:** 2026-01-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Complete the QA generation pipeline with JSONL export in HuggingFace-compatible format and integration into the main workflow. Includes checkpointing for resumable runs. Training and fine-tuning are out of scope.

</domain>

<decisions>
## Implementation Decisions

### JSONL format & structure
- Field names in English: question, answer, source (HuggingFace convention)
- Strict HuggingFace datasets compatibility - `datasets.load_dataset('json', data_files=...)` must work directly
- Rejected pairs: Claude decides level of validation detail to include

### File organization
- Claude decides output directory structure based on project conventions
- Claude decides file naming for passed/rejected outputs
- Claude decides whether to keep or clean intermediate files
- Claude decides whether to include stats.json

### Pipeline integration
- Input: Directory by default, --glob flag for advanced pattern selection
- Error handling: Continue with warnings by default, --fail-fast flag to abort on first error
- Claude decides how --generate-qa integrates with existing pipeline stages
- Claude decides whether --dry-run mode is needed

### Checkpointing & resume
- Claude decides checkpoint granularity (per-document vs per-stage)
- Claude decides resume trigger mechanism (auto-detect vs explicit flag)
- Claude decides checkpoint file location and cleanup behavior

### Claude's Discretion
- Metadata fields per QA pair (balance between provenance and file size)
- Output directory structure (qa/ vs runs/qa/ vs other)
- File naming conventions for passed/rejected outputs
- Intermediate file handling policy
- Stats file inclusion and format
- Dry-run mode implementation
- Checkpoint granularity and state format
- Resume detection and triggering
- Checkpoint cleanup after completion

</decisions>

<specifics>
## Specific Ideas

- HuggingFace compatibility is a hard requirement - the output must work with `datasets.load_dataset()` without adaptation
- Error handling should be configurable: graceful by default (continue processing), but --fail-fast for debugging

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 31-export-integration*
*Context gathered: 2026-01-30*

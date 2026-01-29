# Phase 30: Validation Pipeline - Context

**Gathered:** 2026-01-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Two-stage validation pipeline filtering out hallucinations and low-quality QA pairs. Runs automatically after answer generation. Outputs validated pairs and rejected pairs with reasoning.

</domain>

<decisions>
## Implementation Decisions

### Validation thresholds
- Single composite score (0-1) combining all dimensions
- Fixed threshold at 0.7 to pass (not configurable)
- Validation runs automatically in pipeline after answer generation

### Source verification method
- Hybrid approach: semantic similarity first, LLM judge for borderline cases
- LLM model: gemini-3-flash-preview for verification
- LLM judge provides reasoning (not just pass/fail) for debugging
- Claude's discretion: semantic similarity threshold that triggers LLM review

### Quality dimensions
- Three dimensions: relevans, korrekthet, fullstandighet
- LLM scores each dimension on 0-1 continuous scale
- Separate LLM call from source verification (clear separation)
- Quality scores included in output for ALL pairs (passed and rejected)
- Claude's discretion: dimension weights in composite score

### Failure handling
- Rejected pairs written to separate qa_rejected.jsonl
- Full QA pair included with scores and failure reasoning
- Summary statistics at end: total, passed, failed, pass rate, average scores
- Claude's discretion: whether to implement retry logic for borderline cases

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 30-validation-pipeline*
*Context gathered: 2026-01-29*

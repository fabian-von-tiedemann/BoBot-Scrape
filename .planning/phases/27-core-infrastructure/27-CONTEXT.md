# Phase 27: Core Infrastructure - Context

**Gathered:** 2026-01-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish persona model and QA module structure as foundation for generation pipeline. This phase delivers the data models, configuration, and CLI scaffold that phases 28-31 build upon. No actual QA generation happens here — only the infrastructure.

</domain>

<decisions>
## Implementation Decisions

### Persona modeling
- Rich persona model with all fields: roll, erfarenhet, situation, sprakbakgrund
- Multiple Swedish proficiency levels: native, fluent, intermediate, beginner
- Role focus: underskoterska only (primary target audience)
- Proficiency levels affect question phrasing for realistic variation

### Config format
- Single YAML file: config/personas.yaml
- Auto-generated IDs from role+experience+language combination
- 5 personas in initial config with varied experience/language combos

### CLI interface
- Default output: progress bar + summary stats
- Primary input: converted/ directory (markdown documents)

### Module structure
- One file per phase: persona.py, questions.py, answers.py, validation.py, export.py
- src/qa/ module with __init__.py exposing key classes

### Claude's Discretion
- Whether experience level affects question complexity (for training data diversity)
- Single-document mode (--file) for testing/debugging
- CLI patterns and consistency with existing pipeline.py
- Code sharing with existing src/ modules vs self-contained
- CLI script location (project root vs scripts/)
- Type hints depth and Pydantic usage patterns

</decisions>

<specifics>
## Specific Ideas

- Persona IDs should be readable and traceable in output (auto-generated from fields)
- 5 underskoterskor with different combinations: nyanstald/erfaren x native/intermediate/beginner
- Progress bar during processing for interactive use

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 27-core-infrastructure*
*Context gathered: 2026-01-24*

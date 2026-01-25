# Phase 28: Question Generation - Context

**Gathered:** 2026-01-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate 3-5 diverse, persona-driven questions per document from the knowledge base (1,086 converted markdown documents). Each question is tied to a specific persona perspective and includes source reference. Batch processing with progress bar. Output to intermediate file for inspection before answer generation.

Answer generation, validation, and export are separate phases (29-31).

</domain>

<decisions>
## Implementation Decisions

### Question Style & Format
- Conversational tone — how a care worker would actually ask a colleague ("Hur gör man om..?")
- Mix of scenario-based ("En brukare vägrar ta medicin, vad gör jag?") and general knowledge questions
- Include motivation/context in questions ("Jag är ny på jobbet och undrar...")
- Natural workplace Swedish, including some jargon/abbreviations — how care workers actually talk

### Persona Assignment
- Match persona to document content — pick persona whose situation/role fits the topic best
- Multiple personas per document depends on document length — longer/richer docs get 2-3 personas, short docs get one best-fit persona
- Balance across personas is NOT important — let best-fit dominate even if some personas appear rarely
- Include full persona details in output (role, experience level, language background)

### Question Diversity
- Full range of question types:
  - Factual ("Vad gäller?")
  - Procedural ("Hur gör man?")
  - Situational ("Vad gör jag om...?")
  - Clarification ("Vad menas med...?")
- Lean towards simple complexity — prioritize practical, day-to-day knowledge
- Detect and avoid duplicate/similar questions across documents

### Output Structure
- Format: YAML (human-readable, good for manual inspection/editing)
- Single output file for all questions
- Group questions by document category
- Rich metadata per question:
  - Question text
  - Source document
  - Section reference
  - Question type (factual/procedural/situational/clarification)
  - Persona full details (roll, erfarenhet, situation, språkbakgrund)
  - Confidence score
  - Document category
  - Generation timestamp

### Claude's Discretion
- How to balance coverage vs importance when selecting what to question from a document
- Exact thresholds for "long enough document" to warrant multiple personas
- Similarity detection algorithm for deduplication
- Confidence scoring methodology

</decisions>

<specifics>
## Specific Ideas

- Questions should sound like real conversations between colleagues
- Motivation/context makes questions more realistic and helps calibrate answer depth
- YAML format chosen specifically for easy manual review and editing before answer generation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 28-question-generation*
*Context gathered: 2026-01-25*

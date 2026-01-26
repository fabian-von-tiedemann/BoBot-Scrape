# Phase 29: Answer Generation - Context

**Gathered:** 2026-01-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Generate grounded answers with explicit source citations in plain Swedish. Takes questions from Phase 28 and produces answers directly anchored in source document content using klarsprak principles.

</domain>

<decisions>
## Implementation Decisions

### Citation formatting
- Claude decides citation placement (inline vs footer) based on training data effectiveness
- Multiple sources: cite each claim separately ("X [doc1]. Y [doc2].")
- Citation format: full path with section when available [source:rutiner/handtvatt.md#steg-3]
- Documents without section headings: cite document only, no section marker

### Answer structure
- Target length: short (1-3 sentences) — direct answers only
- Claude decides format (prose vs bullets) based on content type
- Quote sparingly: only for critical/exact wording (dosages, regulations, exact procedures)
- Partial coverage: answer what's covered in source, note limitations for uncovered aspects

### Klarsprak application
- Strict B1 Swedish: max 15 words per sentence, common vocabulary only
- Technical terms: keep and explain ("Dekubitus (ar tryckskada) kraver...")
- Always active voice: "Du tvattar handerna" not "Handerna ska tvattas"
- Direct address: use "du" consistently

### Source extraction
- Semantic search for passage selection (embed question, find similar chunks)
- Retrieve top 5 chunks for context
- Chunk size: medium (512 tokens) — balance precision and context
- Include document metadata: title, author, updated date passed to model

### Claude's Discretion
- Citation placement style (inline vs footer)
- Answer format selection (prose vs bullets)
- Embedding model choice for semantic search
- Exact prompt engineering for answer generation

</decisions>

<specifics>
## Specific Ideas

- Answers should feel like a knowledgeable colleague giving a quick, trustworthy response
- When technical terms are unavoidable, the explanation should be parenthetical and brief

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 29-answer-generation*
*Context gathered: 2026-01-26*

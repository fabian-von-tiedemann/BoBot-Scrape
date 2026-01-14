# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- 🚧 **v2.0 Document Processing Pipeline** — Phases 5-8 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13

## Domain Expertise

None

### 🚧 v2.0 Document Processing Pipeline (In Progress)

**Milestone Goal:** Transform downloaded PDFs and Word docs into well-formatted Markdown with rich metadata for RAG/GraphRAG integration

#### Phase 5: Text Extraction

**Goal**: PDF extraction with pymupdf/pdfplumber, Word extraction with python-docx
**Depends on**: v1.0 complete
**Research**: Likely (new library integrations)
**Research topics**: pymupdf vs pdfplumber comparison, python-docx API patterns
**Plans**: TBD

Plans:
- [ ] 05-01: TBD (run /gsd:plan-phase 5 to break down)

#### Phase 6: Markdown Formatting

**Goal**: Convert extracted text to well-structured Markdown, preserve headings/lists/tables
**Depends on**: Phase 5
**Research**: Unlikely (internal patterns)
**Plans**: TBD

Plans:
- [ ] 06-01: TBD

#### Phase 7: Metadata & AI

**Goal**: Gemini Flash 2 integration for summary/keywords/topics, frontmatter generation
**Depends on**: Phase 6
**Research**: Likely (external API integration)
**Research topics**: Gemini Flash 2 Preview API, google-generativeai SDK, rate limits
**Plans**: TBD

Plans:
- [ ] 07-01: TBD

#### Phase 8: ETL Pipeline

**Goal**: convert.py CLI with options, batch processing, progress tracking
**Depends on**: Phase 7
**Research**: Unlikely (internal patterns, follow scrape.py CLI style)
**Plans**: TBD

Plans:
- [ ] 08-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

| Phase              | Milestone | Plans Complete | Status      | Completed  |
|--------------------|-----------|----------------|-------------|------------|
| 1. Setup           | v1.0      | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery  | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction  | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 4. Download System | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 5. Text Extraction | v2.0      | 0/?            | Not started | -          |
| 6. Markdown Formatting | v2.0  | 0/?            | Not started | -          |
| 7. Metadata & AI   | v2.0      | 0/?            | Not started | -          |
| 8. ETL Pipeline    | v2.0      | 0/?            | Not started | -          |

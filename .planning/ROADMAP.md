# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- ✅ **v2.0 Document Processing Pipeline** — Phases 5-8 (shipped 2026-01-14)
- 🚧 **v2.1 Improvements** — Phases 9-12 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14

## Domain Expertise

None

### 🚧 v2.1 Improvements (In Progress)

**Milestone Goal:** Address deferred issues from v2.0 — clean up URL-encoded filenames, improve frontmatter structure, enhance markdown formatting, and re-convert all documents.

#### Phase 9: Clean Filenames

**Goal**: Decode URL-encoded filenames to readable Swedish characters
**Depends on**: v2.0 complete
**Research**: Unlikely (Python urllib.parse, internal patterns)
**Plans**: TBD

Plans:
- [ ] 09-01: TBD (run /gsd:plan-phase 9 to break down)

#### Phase 10: Frontmatter Polish

**Goal**: Improve YAML frontmatter structure and content quality
**Depends on**: Phase 9
**Research**: Unlikely (YAML formatting, internal patterns)
**Plans**: TBD

Plans:
- [ ] 10-01: TBD

#### Phase 11: Markdown Quality

**Goal**: Enhance markdown formatting, headings, lists, and structure
**Depends on**: Phase 10
**Research**: Unlikely (string manipulation, internal patterns)
**Plans**: TBD

Plans:
- [ ] 11-01: TBD

#### Phase 12: Batch Re-convert

**Goal**: Re-run conversion pipeline on all existing PDFs with improvements
**Depends on**: Phase 11
**Research**: Unlikely (existing convert.py CLI)
**Plans**: TBD

Plans:
- [ ] 12-01: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

| Phase              | Milestone | Plans Complete | Status      | Completed  |
|--------------------|-----------|----------------|-------------|------------|
| 1. Setup           | v1.0      | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery  | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction  | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 4. Download System | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 5. Text Extraction     | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 6. Markdown Formatting | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 7. Metadata & AI   | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 8. ETL Pipeline    | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 9. Clean Filenames | v2.1      | 0/?            | Not started | -          |
| 10. Frontmatter Polish | v2.1  | 0/?            | Not started | -          |
| 11. Markdown Quality | v2.1    | 0/?            | Not started | -          |
| 12. Batch Re-convert | v2.1    | 0/?            | Not started | -          |

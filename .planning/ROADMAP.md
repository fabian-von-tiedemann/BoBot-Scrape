# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- ✅ **v2.0 Document Processing Pipeline** — Phases 5-8 (shipped 2026-01-14)
- ✅ **v2.1 Improvements** — Phases 9-10 (shipped 2026-01-14)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14

## Domain Expertise

None

### ✅ v2.1 Improvements (Complete)

**Milestone Goal:** Address deferred issues from v2.0 — clean up output quality and re-convert all documents.

#### Phase 9: Output Quality ✓

**Goal**: Fix URL-encoded filenames, improve frontmatter, enhance markdown formatting
**Depends on**: v2.0 complete
**Research**: Unlikely (Python stdlib, internal patterns)
**Plans**: 1/1

Plans:

- [x] 09-01: URL decoding and source_url lookup

#### Phase 10: Batch Re-convert ✓

**Goal**: Re-run conversion pipeline on all existing PDFs with improvements
**Depends on**: Phase 9
**Research**: Unlikely (existing convert.py CLI)
**Plans**: 1/1

Plans:

- [x] 10-01: Re-convert all documents

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10

| Phase                  | Milestone | Plans Complete | Status      | Completed  |
|------------------------|-----------|----------------|-------------|------------|
| 1. Setup               | v1.0      | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery      | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction      | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 4. Download System     | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 5. Text Extraction     | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 6. Markdown Formatting | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 7. Metadata & AI       | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 8. ETL Pipeline        | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 9. Output Quality      | v2.1      | 1/1            | Complete    | 2026-01-14 |
| 10. Batch Re-convert   | v2.1      | 1/1            | Complete    | 2026-01-14 |

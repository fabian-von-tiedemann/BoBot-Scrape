# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- ✅ **v2.0 Document Processing Pipeline** — Phases 5-8 (shipped 2026-01-14)
- ✅ **v2.1 Improvements** — Phases 9-10 (shipped 2026-01-14)
- 🚧 **v2.2 Frontmatter Enrichment** — Phases 11-14 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14
- ✅ [v2.1 Improvements](milestones/v2.1-ROADMAP.md) (Phases 9-10) — SHIPPED 2026-01-14

## Domain Expertise

None

<details>
<summary>✅ v2.1 Improvements (Phases 9-10) — SHIPPED 2026-01-14</summary>

- [x] Phase 9: Output Quality (1/1 plan) — completed 2026-01-14
- [x] Phase 10: Batch Re-convert (1/1 plan) — completed 2026-01-14

See [milestones/v2.1-ROADMAP.md](milestones/v2.1-ROADMAP.md) for full details.

</details>

### 🚧 v2.2 Frontmatter Enrichment (In Progress)

**Milestone Goal:** Berika markdown-frontmatter med verksamhet och rutinkategori för bättre dokumentorganisation och AI-sökning.

#### Phase 11: Rutin Scraper Update

**Goal**: Uppdatera scraper för att extrahera rutinkategorier från webbsidor och spara till CSV
**Depends on**: Previous milestone complete
**Research**: Unlikely (befintlig scraper-kod, intern förbättring)
**Plans**: 1/1 complete

Plans:
- [x] 11-01: Add verksamhet column to CSV export — completed 2026-01-14

#### Phase 12: Frontmatter Properties

**Goal**: Lägg till verksamhet och rutin properties i markdown-konvertering
**Depends on**: Phase 11
**Research**: Unlikely (befintlig konverteringskod)
**Plans**: 1/1 complete

Plans:
- [x] 12-01: Add verksamhet and rutin to frontmatter — completed 2026-01-14

#### Phase 13: Batch Apply

**Goal**: Kör om konvertering på alla dokument med nya frontmatter-properties
**Depends on**: Phase 12
**Research**: Unlikely (samma mönster som Phase 10)
**Plans**: 1/1 complete

Plans:
- [x] 13-01: Re-convert all documents with verksamhet/rutin — completed 2026-01-14

#### Phase 14: Fix Verksamhet/Rutin Hierarchy

**Goal**: Korrigera verksamhet/rutin-logiken - scrapa underkategorier från webbsidor
**Depends on**: Phase 13
**Research**: Likely (behöver förstå HTML-struktur för underkategorier)
**Plans**: TBD

Plans:
- [ ] 14-01: TBD (run /gsd:plan-phase 14 to break down)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → ... → 10 → 11 → 12 → 13 → 14

| Phase                    | Milestone | Plans Complete | Status      | Completed  |
|--------------------------|-----------|----------------|-------------|------------|
| 1. Setup                 | v1.0      | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery        | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction        | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 4. Download System       | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 5. Text Extraction       | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 6. Markdown Formatting   | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 7. Metadata & AI         | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 8. ETL Pipeline          | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 9. Output Quality        | v2.1      | 1/1            | Complete    | 2026-01-14 |
| 10. Batch Re-convert     | v2.1      | 1/1            | Complete    | 2026-01-14 |
| 11. Rutin Scraper Update | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 12. Frontmatter Props    | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 13. Batch Apply          | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 14. Fix Hierarchy        | v2.2      | 0/?            | Not started | -          |

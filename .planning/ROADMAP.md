# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- ✅ **v2.0 Document Processing Pipeline** — Phases 5-8 (shipped 2026-01-14)
- ✅ **v2.1 Improvements** — Phases 9-10 (shipped 2026-01-14)
- ✅ **v2.2 Frontmatter Enrichment** — Phases 11-14 (shipped 2026-01-14)
- ✅ **v2.3 Frontmatter Schema Upgrade** — Phases 15-17 (shipped 2026-01-14)
- ✅ **v2.4 Knowledge Base Delivery** — Phase 18 (shipped 2026-01-14)
- 🚧 **v2.5 System Prompt Generation** — Phases 19-21 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14
- ✅ [v2.1 Improvements](milestones/v2.1-ROADMAP.md) (Phases 9-10) — SHIPPED 2026-01-14
- ✅ [v2.2 Frontmatter Enrichment](milestones/v2.2-ROADMAP.md) (Phases 11-14) — SHIPPED 2026-01-14
- ✅ [v2.3 Frontmatter Schema Upgrade](milestones/v2.3-ROADMAP.md) (Phases 15-17) — SHIPPED 2026-01-14
- ✅ [v2.4 Knowledge Base Delivery](milestones/v2.4-ROADMAP.md) (Phase 18) — SHIPPED 2026-01-14

### 🚧 v2.5 System Prompt Generation (In Progress)

**Milestone Goal:** Generera skräddarsydda systemprompts per enhet/område baserat på dokumentinnehåll för AI-assistenten.

#### Phase 19: Frontmatter Indexer ✅

**Goal**: Extrahera frontmatter från alla markdown-filer per mapp och skapa index-dokument
**Depends on**: Previous milestone complete
**Research**: Unlikely (befintlig frontmatter-struktur, Python YAML-parsing)
**Plans**: 1/1 complete

- [x] 19-01: Create frontmatter indexer and KB indexer CLI — completed 2026-01-14

#### Phase 20: System Prompt Generator

**Goal**: Generera enhet-specifika systemprompts med Gemini baserat på index-dokumenten
**Depends on**: Phase 19
**Research**: Likely (prompt engineering för optimal systemprompt-struktur)
**Research topics**: Best practices för systemprompts, hur strukturera kontext för RAG-assistenter
**Plans**: TBD

- [ ] 20-01: TBD (run /gsd:plan-phase 20 to break down)

#### Phase 21: General Prompt Template

**Goal**: Skapa generell systemprompt-del som gäller alla enheter + kombinera med enhet-specifika delar
**Depends on**: Phase 20
**Research**: Unlikely (intern promptstruktur, ingen extern integration)
**Plans**: TBD

- [ ] 21-01: TBD (run /gsd:plan-phase 21 to break down)

## Domain Expertise

None

<details>
<summary>✅ v2.1 Improvements (Phases 9-10) — SHIPPED 2026-01-14</summary>

- [x] Phase 9: Output Quality (1/1 plan) — completed 2026-01-14
- [x] Phase 10: Batch Re-convert (1/1 plan) — completed 2026-01-14

See [milestones/v2.1-ROADMAP.md](milestones/v2.1-ROADMAP.md) for full details.

</details>

<details>
<summary>✅ v2.2 Frontmatter Enrichment (Phases 11-14) — SHIPPED 2026-01-14</summary>

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
**Plans**: 2/2 complete

Plans:
- [x] 14-01: Extract subcategory headings from HTML DOM — completed 2026-01-14
- [x] 14-02: Re-convert all documents with correct hierarchy — completed 2026-01-14

</details>

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → ... → 17 → 18

| Phase                     | Milestone | Plans Complete | Status      | Completed  |
|---------------------------|-----------|----------------|-------------|------------|
| 1. Setup                  | v1.0      | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery         | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction         | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 4. Download System        | v1.0      | 1/1            | Complete    | 2026-01-13 |
| 5. Text Extraction        | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 6. Markdown Formatting    | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 7. Metadata & AI          | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 8. ETL Pipeline           | v2.0      | 1/1            | Complete    | 2026-01-14 |
| 9. Output Quality         | v2.1      | 1/1            | Complete    | 2026-01-14 |
| 10. Batch Re-convert      | v2.1      | 1/1            | Complete    | 2026-01-14 |
| 11. Rutin Scraper Update  | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 12. Frontmatter Props     | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 13. Batch Apply           | v2.2      | 1/1            | Complete    | 2026-01-14 |
| 14. Fix Hierarchy         | v2.2      | 2/2            | Complete    | 2026-01-14 |
| 15. Scraper Hierarchy     | v2.3      | 1/1            | Complete    | 2026-01-14 |
| 16. Frontmatter Upgrade   | v2.3      | 1/1            | Complete    | 2026-01-14 |
| 17. Batch Re-convert      | v2.3      | 1/1            | Complete    | 2026-01-14 |
| 18. KB Delivery           | v2.4      | 1/1            | Complete    | 2026-01-14 |
| 19. Frontmatter Indexer   | v2.5      | 1/1            | Complete    | 2026-01-14 |
| 20. System Prompt Gen     | v2.5      | 0/?            | Not started | -          |
| 21. General Prompt        | v2.5      | 0/?            | Not started | -          |

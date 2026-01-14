# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-01-13)
- ✅ **v2.0 Document Processing Pipeline** — Phases 5-8 (shipped 2026-01-14)
- ✅ **v2.1 Improvements** — Phases 9-10 (shipped 2026-01-14)
- ✅ **v2.2 Frontmatter Enrichment** — Phases 11-14 (shipped 2026-01-14)
- 🚧 **v2.3 Frontmatter Schema Upgrade** — Phases 15-17 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14
- ✅ [v2.1 Improvements](milestones/v2.1-ROADMAP.md) (Phases 9-10) — SHIPPED 2026-01-14
- ✅ [v2.2 Frontmatter Enrichment](milestones/v2.2-ROADMAP.md) (Phases 11-14) — SHIPPED 2026-01-14

### 🚧 v2.3 Frontmatter Schema Upgrade (In Progress)

**Milestone Goal:** Uppgradera frontmatter-schemat med hierarkisk kategori/underkategori, AI-klassificerad dokumenttyp och extraherat uppdateringsdatum.

#### Phase 15: Scraper Hierarchy Update

**Goal**: Uppdatera scraper för att extrahera category/subcategory-hierarkin från nästlade collapsible-sektioner
**Depends on**: Previous milestone complete
**Research**: Likely (behöver förstå exakt HTML-nästlingsstruktur)
**Research topics**: HTML DOM-struktur för nästlade sol-collapsible sektioner
**Plans**: 1/1 complete

Plans:
- [x] 15-01: Rename CSV columns to category/subcategory — completed 2026-01-14

#### Phase 16: Converter Frontmatter Upgrade

**Goal**: Uppdatera frontmatter-schemat med category, subcategory, document_type och updated_date
**Depends on**: Phase 15
**Research**: Unlikely (befintlig konverteringskod och AI-integration)
**Plans**: TBD

Plans:
- [ ] 16-01: TBD

#### Phase 17: Batch Re-convert

**Goal**: Kör om konvertering på alla dokument med nya frontmatter-schemat
**Depends on**: Phase 16
**Research**: Unlikely (samma mönster som Phase 10 och 13)
**Plans**: TBD

Plans:
- [ ] 17-01: TBD

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
Phases execute in numeric order: 1 → 2 → ... → 14 → 15 → 16 → 17

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
| 16. Frontmatter Upgrade   | v2.3      | 0/?            | Not started | -          |
| 17. Batch Re-convert      | v2.3      | 0/?            | Not started | -          |

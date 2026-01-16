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
- ✅ **v2.5 System Prompt Generation** — Phases 19-21 (shipped 2026-01-14)
- ✅ **v3.0 Digi Commands** — Phase 22 (shipped 2026-01-14)
- ✅ **v3.1 Improvements** — Phase 23 (shipped 2026-01-15)
- 🚧 **v4.0 Pipeline Refactor** — Phases 24-26 (in progress)

## Completed Milestones

- ✅ [v1.0 MVP](milestones/v1.0-ROADMAP.md) (Phases 1-4) — SHIPPED 2026-01-13
- ✅ [v2.0 Document Processing Pipeline](milestones/v2.0-ROADMAP.md) (Phases 5-8) — SHIPPED 2026-01-14
- ✅ [v2.1 Improvements](milestones/v2.1-ROADMAP.md) (Phases 9-10) — SHIPPED 2026-01-14
- ✅ [v2.2 Frontmatter Enrichment](milestones/v2.2-ROADMAP.md) (Phases 11-14) — SHIPPED 2026-01-14
- ✅ [v2.3 Frontmatter Schema Upgrade](milestones/v2.3-ROADMAP.md) (Phases 15-17) — SHIPPED 2026-01-14
- ✅ [v2.4 Knowledge Base Delivery](milestones/v2.4-ROADMAP.md) (Phase 18) — SHIPPED 2026-01-14
- ✅ [v2.5 System Prompt Generation](milestones/v2.5-ROADMAP.md) (Phases 19-21) — SHIPPED 2026-01-14

<details>
<summary>✅ v2.5 System Prompt Generation (Phases 19-21) — SHIPPED 2026-01-14</summary>

**Milestone Goal:** Generera skräddarsydda systemprompts per enhet/område baserat på dokumentinnehåll för AI-assistenten.

- [x] Phase 19: Frontmatter Indexer (1/1 plan) — completed 2026-01-14
- [x] Phase 20: System Prompt Generator (1/1 plan) — completed 2026-01-14
- [x] Phase 21: General Prompt Template (1/1 plan) — completed 2026-01-14

See [milestones/v2.5-ROADMAP.md](milestones/v2.5-ROADMAP.md) for full details.

</details>

### ✅ v3.0 Digi Commands (Complete)

**Milestone Goal:** Create reusable Claude commands for pushing knowledge base content to GitHub.

#### Phase 22: KB Push Command

**Goal**: Create /digi:push-kb command with full sync behavior (converted/, indexes/, prompts/)
**Depends on**: Previous milestone complete
**Plans**: 1/1 complete

Plans:

- [x] 22-01: Create push-kb command — completed 2026-01-14

### ✅ v3.1 Improvements (Complete)

**Milestone Goal:** Förbättra prestanda genom parallella AI-anrop för snabbare dokumentaugmentering.

#### Phase 23: Parallel AI Calls

**Goal**: Implementera asynkron batch-processing med parallella Gemini-anrop
**Depends on**: Previous milestone complete
**Research**: Unlikely (Python asyncio/concurrent.futures är standard patterns)
**Plans**: 1/1 complete

Plans:

- [x] 23-01: Implement parallel Gemini API calls — completed 2026-01-15

### 🚧 v4.0 Pipeline Refactor (In Progress)

**Milestone Goal:** Generalisera ETL-flödet till en versionshanterbar pipeline med timestampade output-mappar och stöd för inkrementella uppdateringar.

#### Phase 24: Pipeline Runner

**Goal**: Unified CLI that orchestrates all stages (scrape, convert, index, prompts) with timestamped output directories
**Depends on**: Previous milestone complete
**Research**: Unlikely (internal patterns, existing scripts to orchestrate)
**Plans**: 1/1 complete

Plans:

- [x] 24-01: Create pipeline.py CLI with timestamped run directories — completed 2026-01-16

#### Phase 25: Incremental Updates

**Goal**: Detect new/changed documents and process only those (skip already-processed files)
**Depends on**: Phase 24
**Research**: Unlikely (file comparison, existing skip-existing pattern)
**Plans**: 1/1 complete

Plans:

- [x] 25-01: Implement manifest-based diff detection and incremental convert — completed 2026-01-16

#### Phase 26: KB Sync Integration

**Goal**: Automatic push to bobot-kb repo after pipeline run completes
**Depends on**: Phase 25
**Research**: Unlikely (existing /digi:push-kb command to integrate)
**Plans**: 1/1 complete

Plans:

- [x] 26-01: Add --push-kb flag and sync_to_kb() function — completed 2026-01-16

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
| 20. System Prompt Gen     | v2.5      | 1/1            | Complete    | 2026-01-14 |
| 21. General Prompt        | v2.5      | 1/1            | Complete    | 2026-01-14 |
| 22. KB Push Command       | v3.0      | 1/1            | Complete    | 2026-01-14 |
| 23. Parallel AI Calls     | v3.1      | 1/1            | Complete    | 2026-01-15 |
| 24. Pipeline Runner       | v4.0      | 1/1            | Complete    | 2026-01-16 |
| 25. Incremental Updates   | v4.0      | 1/1            | Complete    | 2026-01-16 |
| 26. KB Sync Integration   | v4.0      | 1/1            | Complete    | 2026-01-16 |

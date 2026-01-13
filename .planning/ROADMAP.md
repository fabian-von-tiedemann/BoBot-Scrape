# Roadmap: BoBot-Scrape

## Overview

En PDF-scraper som ansluter till användarens befintliga Chrome-session, navigerar Botkyrka kommuns intranät, och laddar ner alla rutindokument organiserade i mappar. Från setup till fungerande nedladdning på fyra faser.

## Domain Expertise

None

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Setup** - Python-miljö, Playwright, Chrome CDP-anslutning
- [x] **Phase 2: Page Discovery** - Navigera startsida, extrahera kategorilänkar
- [x] **Phase 3: PDF Extraction** - Följ kategorier, hitta alla PDF-länkar
- [x] **Phase 4: Download System** - Ladda ner PDF:er till organiserad mappstruktur

## Phase Details

### Phase 1: Setup
**Goal**: Fungerande Python-script som kan ansluta till körande Chrome via CDP
**Depends on**: Nothing (first phase)
**Research**: Likely (Playwright CDP connection)
**Research topics**: Playwright connect_over_cdp API, Chrome remote debugging flags, session reuse patterns
**Plans**: TBD

Plans:
- [x] 01-01: Python environment and dependencies
- [x] 01-02: Chrome CDP connection

### Phase 2: Page Discovery
**Goal**: Scriptet kan navigera till startsidan och extrahera alla kategorilänkar
**Depends on**: Phase 1
**Research**: Unlikely (standard Playwright navigation)
**Plans**: TBD

Plans:
- [x] 02-01: Navigate and extract category links

### Phase 3: PDF Extraction
**Goal**: Scriptet kan följa varje kategorilänk och hitta alla PDF-länkar
**Depends on**: Phase 2
**Research**: Unlikely (standard link extraction)
**Plans**: TBD

Plans:
- [x] 03-01: Follow categories and extract PDF links

### Phase 4: Download System
**Goal**: Alla PDF:er nedladdade och organiserade i mappar baserat på kategori
**Depends on**: Phase 3
**Research**: Unlikely (file download/folder creation)
**Plans**: TBD

Plans:
- [x] 04-01: Download PDFs to category folders

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase              | Plans Complete | Status      | Completed  |
|--------------------|----------------|-------------|------------|
| 1. Setup           | 2/2            | Complete    | 2026-01-13 |
| 2. Page Discovery  | 1/1            | Complete    | 2026-01-13 |
| 3. PDF Extraction  | 1/1            | Complete    | 2026-01-13 |
| 4. Download System | 1/1            | Complete    | 2026-01-13 |

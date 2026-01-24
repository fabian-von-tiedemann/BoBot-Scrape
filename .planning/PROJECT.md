# BoBot-Scrape

## What This Is

En komplett ETL-pipeline för rutindokument från Botkyrka kommuns intranät (BoTwebb). Ansluter till användarens befintliga Chrome-session via CDP, laddar ner alla PDF:er och Word-dokument, konverterar till AI-berikad Markdown, genererar verksamhetsspecifika system prompts, och synkar automatiskt till kunskapsbas-repo för AI-assistenter. Genererar även QA-par från kunskapsbasen för AI-assistentträning.

## Core Value

Alla PDF:er nedladdade och konverterade — ingen PDF ska missas, oavsett hur sidstrukturen ser ut.

## Current Milestone: v5.0 QA Generation Pipeline

**Goal:** Generera tusentals fråga/svar-par från kunskapsbasen för att bygga affärsregler och evalueringsdata till AI-assistenten.

**Target features:**
- Persona-driven frågor (roll + situation: stressad undersköterska, ny hemtjänstpersonal, nattjour)
- Svar grundade i faktiska dokument med källreferens
- Tvåstegs validering (källverifiering + kvalitetsbedömning)
- Adaptive svarsformat (kort för fakta, stegvis för instruktioner)
- Export för prompt-kontext och evaluering

## Requirements

### Validated

**v1.0 MVP:**
- ✓ Ansluta till befintlig Chrome-session med aktiv inloggning — v1.0
- ✓ Navigera till startsidan och extrahera alla kategorilänkar — v1.0
- ✓ Följa varje kategorilänk och hitta alla PDF-länkar — v1.0
- ✓ Ladda ner varje PDF till rätt kategorimapp — v1.0
- ✓ Skapa mappstruktur baserad på kategorilänkarnas namn — v1.0

**v2.0 Document Processing Pipeline:**
- ✓ Extrahera text från PDF-dokument (pymupdf) — v2.0
- ✓ Extrahera text från Word-dokument (python-docx) — v2.0
- ✓ Konvertera text till välstrukturerad Markdown — v2.0
- ✓ Generera AI-metadata med Gemini (summary, keywords, topics) — v2.0
- ✓ CLI för batch-konvertering med progress-tracking — v2.0

**v2.1 Improvements:**

- ✓ URL-decoded filenames in converted output — v2.1
- ✓ source_url field in frontmatter for AI agents — v2.1
- ✓ Human-readable Swedish titles — v2.1

**v2.2 Frontmatter Enrichment:**

- ✓ Verksamhet property in frontmatter (organizational unit) — v2.2
- ✓ Rutin property in frontmatter (subcategory heading) — v2.2
- ✓ DOM walker for collapsible section header extraction — v2.2
- ✓ Notification banner filtering — v2.2

**v2.3 Frontmatter Schema Upgrade:**

- ✓ category/subcategory naming convention for standardized hierarchy — v2.3
- ✓ updated_date AI extraction for document currency tracking — v2.3

**v2.4 Knowledge Base Delivery:**

- ✓ Private GitHub repo (bobot-kb) with all converted documents — v2.4
- ✓ README documenting KB structure and frontmatter schema — v2.4

**v2.5 System Prompt Generation:**

- ✓ Frontmatter indexer extracting metadata from 1,086 documents — v2.5
- ✓ 15 verksamhet-specific index files for AI context — v2.5
- ✓ Gemini-powered system prompt generator — v2.5
- ✓ General Swedish system prompt template (6 sections) — v2.5
- ✓ 15 combined prompts ready for AI assistant deployment — v2.5

**v3.0 Digi Commands:**

- ✓ /digi:push-kb command with full sync behavior — v3.0

**v3.1 Improvements:**

- ✓ Parallel Gemini API calls for faster batch conversion — v3.1

**v4.0 Pipeline Refactor:**

- ✓ Unified pipeline.py CLI orchestrating all 5 ETL stages — v4.0
- ✓ Timestamped run directories under runs/ — v4.0
- ✓ Manifest-based diff detection with MD5 hashes — v4.0
- ✓ Incremental convert mode processing only changed docs — v4.0
- ✓ Automatic GitHub sync with --push-kb flag — v4.0
- ✓ Dry-run preview mode for sync operations — v4.0

### Active

**v5.0 QA Generation Pipeline:**
- [ ] Persona-modell med roll + situation för realistiska frågor
- [ ] Frågegenerering från KB-dokument med Gemini
- [ ] Svarsgrundning i faktiska dokument med källreferens
- [ ] Tvåstegs validering (källcheck + kvalitetsbedömning)
- [ ] Adaptivt svarsformat baserat på frågetyp
- [ ] Export-format för prompt-kontext och evalueringsdata
- [ ] Pipeline för 1000-tals QA-par

### Out of Scope

- ~~Inkrementella uppdateringar (bara ladda ner nya/ändrade)~~ — **Implemented in v4.0** (manifest-based diff detection)
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Current State:** Shipped v4.0 with ~3,036 LOC Python (pipeline.py, scrape.py, convert.py, index_kb.py, generate_prompts.py, combine_prompts.py, src/ modules).

**Tech stack:**
- Python 3.11
- Playwright (sync API) — Chrome CDP connection
- pymupdf (fitz) — PDF text extraction
- python-docx — Word text extraction
- google-genai — Gemini API for AI metadata
- argparse, python-dotenv
- subprocess, hashlib — Pipeline orchestration

**Capabilities:**
- Connect to Chrome via CDP (preserves user SAML session)
- Extract 15 rutiner categories from intranet
- Find and download all PDF/Word documents (~1149 files)
- Extract text from PDF and DOCX files
- Convert to structured Markdown with Swedish heading detection
- Generate AI metadata (summary, keywords, topics, document_type, updated_date)
- Batch convert with YAML frontmatter output (category/subcategory hierarchy)
- Generate verksamhet-specific index files from frontmatter
- Generate AI-powered system prompts per verksamhet
- Combine general + specific prompts for AI assistant deployment
- **Unified pipeline CLI with timestamped run directories**
- **Manifest-based incremental updates (only process changed docs)**
- **Automatic sync to bobot-kb GitHub repository**

**Usage:**
```bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug"

# Run full pipeline (recommended)
.venv/bin/python pipeline.py                           # Full run: scrape → convert → index → prompts → sync
.venv/bin/python pipeline.py --skip-scrape             # Skip scrape, use existing downloads
.venv/bin/python pipeline.py --prev-run runs/latest    # Incremental: only process changes
.venv/bin/python pipeline.py --push-kb                 # Push to bobot-kb after completion
.venv/bin/python pipeline.py --push-kb --dry-run       # Preview sync without pushing

# Individual scripts (legacy)
.venv/bin/python scrape.py           # Download new files
.venv/bin/python convert.py          # Convert with AI metadata
```

## Constraints

- **Webbläsare**: Chrome (användarens befintliga profil med aktiv session)
- **Autentisering**: Måste använda befintlig session — ingen inloggningsautomatisering
- **AI API**: Gemini API key krävs för metadata-generering (optional)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Playwright över Selenium | Bättre CDP-stöd för att ansluta till körande Chrome | ✓ Good |
| Python som språk | Enkelt, Playwright har bra Python-stöd | ✓ Good |
| Två-nivå-traversering | Startsida → kategorisidor → PDF:er | ✓ Good |
| sync_playwright API | Enklare för script, ingen async-komplexitet | ✓ Good |
| --user-data-dir för Chrome | Krävs för remote debugging | ✓ Good |
| Exact-match category filtering | Robust mot sidändringar | ✓ Good |
| Skip existing files by default | Incremental downloads utan manuell flagga | ✓ Good |
| CSV export med URLs | Integration med assistants/externa verktyg | ✓ Good |
| pymupdf över pdfplumber | Bättre textkvalitet för svenska dokument | ✓ Good |
| Pydantic för Gemini output | Type-safe structured responses | ✓ Good |
| Graceful AI degradation | Fortsätt utan metadata om API misslyckas | ✓ Good |
| YAML frontmatter format | Kompatibelt med static site generators | ✓ Good |
| URL decode display names only | Keep source paths URL-encoded for disk traceability | ✓ Good |
| source_url as separate field | Enables AI agents to reference original documents | ✓ Good |
| verksamhet/rutin hierarchy | Organizational metadata for document categorization | ✓ Good |
| Collapsible header extraction | DOM walker finds sol-collapsible-header-text divs | ✓ Good |
| Banner blocklist | Filters notification messages from rutin values | ✓ Good |
| category/subcategory naming | Standardized hierarchy terminology | ✓ Good |
| updated_date AI extraction | Track document currency via AI | ✓ Good |
| Private bobot-kb repo | Secure knowledge base delivery | ✓ Good |
| Verksamhet-specific prompts | AI-generated per-unit guidance | ✓ Good |
| General prompt template | 6 Swedish sections for consistency | ✓ Good |
| sys.executable for subprocess | Ensures correct Python interpreter in venv | ✓ Good |
| Timestamped run directories | Versioned output under runs/YYYY-MM-DD-HHMM/ | ✓ Good |
| MD5 hash for URL comparison | Fast, deterministic, no security concerns | ✓ Good |
| Manifest-based diff detection | Track changes between pipeline runs | ✓ Good |
| Fallback source directories | Prefer run_dir, fall back to root | ✓ Good |
| Git CLI over gh CLI | Standard git more portable than GitHub CLI | ✓ Good |

---
*Last updated: 2026-01-24 after v5.0 milestone start*

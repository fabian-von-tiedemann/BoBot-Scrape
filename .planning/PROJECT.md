# BoBot-Scrape

## What This Is

En PDF-scraper och dokumentprocessor som automatiserar nedladdning och konvertering av rutindokument från Botkyrka kommuns intranät (BoTwebb). Ansluter till användarens befintliga Chrome-session via CDP för att hantera SAML-autentisering, laddar ner alla PDF:er och Word-dokument, och konverterar dem till AI-berikad Markdown.

## Core Value

Alla PDF:er nedladdade och konverterade — ingen PDF ska missas, oavsett hur sidstrukturen ser ut.

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

### Active

(None — v2.5 complete, project feature-complete)

### Out of Scope

- Inkrementella uppdateringar (bara ladda ner nya/ändrade) — delvis implementerat (skip existing by default)
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Current State:** Shipped v2.5 with ~1,200 LOC Python (scrape.py, convert.py, index_kb.py, generate_prompts.py, combine_prompts.py, src/ modules).

**Tech stack:**
- Python 3.11
- Playwright (sync API) — Chrome CDP connection
- pymupdf (fitz) — PDF text extraction
- python-docx — Word text extraction
- google-genai — Gemini API for AI metadata
- argparse, python-dotenv

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

**Usage:**
```bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug"

# Download documents
.venv/bin/python scrape.py           # Download new files
.venv/bin/python scrape.py --force   # Re-download all

# Convert to Markdown
.venv/bin/python convert.py          # Convert with AI metadata
.venv/bin/python convert.py --skip-ai  # Fast, no API calls
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

---
*Last updated: 2026-01-14 after v2.5 milestone*

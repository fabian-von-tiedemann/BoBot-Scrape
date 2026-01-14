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

### Active

(None — v2.0 complete, planning next milestone)

### Out of Scope

- Inkrementella uppdateringar (bara ladda ner nya/ändrade) — delvis implementerat (skip existing by default)
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Current State:** Shipped v2.0 with 822 LOC Python (src/ modules + CLIs).

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
- Generate AI metadata (summary, keywords, topics, document_type)
- Batch convert with YAML frontmatter output

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

---
*Last updated: 2026-01-14 after v2.0 milestone*

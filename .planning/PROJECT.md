# BoBot-Scrape

## What This Is

En PDF-scraper som automatiserar nedladdning av rutindokument från Botkyrka kommuns intranät (BoTwebb). Ansluter till användarens befintliga Chrome-session via CDP för att hantera SAML-autentisering och laddar ner alla PDF:er och Word-dokument organiserade i mappar baserat på kategori.

## Core Value

Alla PDF:er nedladdade — ingen PDF ska missas, oavsett hur sidstrukturen ser ut.

## Requirements

### Validated

- ✓ Ansluta till befintlig Chrome-session med aktiv inloggning — v1.0
- ✓ Navigera till startsidan och extrahera alla kategorilänkar — v1.0
- ✓ Följa varje kategorilänk och hitta alla PDF-länkar — v1.0
- ✓ Ladda ner varje PDF till rätt kategorimapp — v1.0
- ✓ Skapa mappstruktur baserad på kategorilänkarnas namn — v1.0

### Active

(None — v1.0 MVP complete)

### Out of Scope

- Inkrementella uppdateringar (bara ladda ner nya/ändrade) — delvis implementerat (skip existing by default)
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Shipped v1.0 with 375 LOC Python.**

**Tech stack:** Python 3.11, Playwright (sync API), argparse, urllib.parse

**Capabilities:**
- Connect to Chrome via CDP (preserves user SAML session)
- Extract 15 rutiner categories from intranet
- Find all PDF and Word documents (~1195 files)
- Download to organized folder structure (downloads/<category>/)
- Export CSV with URLs for assistant integration

**Usage:**
```bash
# Start Chrome with remote debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug"

# Run scraper
.venv/bin/python scrape.py           # Download new files
.venv/bin/python scrape.py --scan-only  # CSV only
.venv/bin/python scrape.py --force      # Re-download all
```

## Constraints

- **Webbläsare**: Chrome (användarens befintliga profil med aktiv session)
- **Autentisering**: Måste använda befintlig session — ingen inloggningsautomatisering

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

---
*Last updated: 2026-01-13 after v1.0 milestone*

# BoBot-Scrape

## What This Is

En komplett ETL- och QA-pipeline för rutindokument från Botkyrka kommuns intranät (BoTwebb). Ansluter till användarens befintliga Chrome-session via CDP, laddar ner alla PDF:er och Word-dokument, konverterar till AI-berikad Markdown, genererar verksamhetsspecifika system prompts, synkar automatiskt till kunskapsbas-repo, och genererar validerade QA-par med persona-drivna frågor, grundade svar och tvåstegs kvalitetsvalidering för AI-assistentträning.

## Core Value

Alla PDF:er nedladdade och konverterade — ingen PDF ska missas, oavsett hur sidstrukturen ser ut.

## Latest Milestone: v5.0 QA Generation Pipeline (Shipped 2026-02-19)

**Delivered:** Komplett QA-pipeline som genererar validerade fråga/svar-par från 1,086 kunskapsbas-dokument med persona-drivna frågor, grundade svar, och tvåstegs kvalitetsvalidering.

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

**v5.0 QA Generation Pipeline:**

- ✓ Persona-modell med roll + situation för realistiska frågor — v5.0
- ✓ Frågegenerering från KB-dokument med Gemini — v5.0
- ✓ Svarsgrundning i faktiska dokument med källreferens — v5.0
- ✓ Tvåstegs validering (källcheck + kvalitetsbedömning) — v5.0
- ✓ Export-format för prompt-kontext och evalueringsdata (HuggingFace JSONL) — v5.0
- ✓ Pipeline för QA-par med checkpointing och resume — v5.0

### Active

(No active requirements — define with `/gsd:new-milestone`)

### Out of Scope

- ~~Inkrementella uppdateringar (bara ladda ner nya/ändrade)~~ — **Implemented in v4.0** (manifest-based diff detection)
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Current State:** Shipped v5.0 with ~5,662 LOC Python (pipeline.py, scrape.py, convert.py, index_kb.py, generate_prompts.py, combine_prompts.py, generate_qa.py, src/ modules including src/qa/).

**Tech stack:**
- Python 3.11
- Playwright (sync API) — Chrome CDP connection
- pymupdf (fitz) — PDF text extraction
- python-docx — Word text extraction
- google-genai — Gemini API for AI metadata and QA generation
- sentence-transformers — KBLab Swedish SBERT embeddings
- faiss-cpu — Vector search for semantic retrieval
- pydantic — Structured LLM output and data models
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
- Unified pipeline CLI with timestamped run directories
- Manifest-based incremental updates (only process changed docs)
- Automatic sync to bobot-kb GitHub repository
- **Persona-driven QA question generation from knowledge base documents**
- **Swedish semantic retrieval with FAISS and KBLab SBERT embeddings**
- **Extraction-style answer generation with inline source citations**
- **Two-stage QA validation (semantic similarity + LLM-as-judge)**
- **HuggingFace-compatible JSONL export with metadata**
- **Resumable QA pipeline with stage-level checkpointing**

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
.venv/bin/python pipeline.py --generate-qa             # Include QA generation pipeline

# QA generation (standalone)
.venv/bin/python generate_qa.py                        # Generate questions
.venv/bin/python generate_qa.py --build-index          # Build FAISS index
.venv/bin/python generate_qa.py --answers              # Generate answers
.venv/bin/python generate_qa.py --validate             # Validate QA pairs
.venv/bin/python generate_qa.py --export               # Export to HuggingFace JSONL

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
| Persona ID {roll}-{erfarenhet}-{sprakbakgrund} | Human-readable, deterministic computed field | ✓ Good |
| gemini-2.0-flash for QA | gemini-3-flash-preview not yet available | ✓ Good |
| KBLab/sentence-bert-swedish-cased | Best Swedish embedding model (0.918 Pearson) | ✓ Good |
| 512-token chunks, 128 overlap | Microsoft RAG guidelines for semantic retrieval | ✓ Good |
| FAISS IndexFlatIP | Cosine similarity via L2 normalization | ✓ Good |
| Extraction-style prompting | Direct quotes over paraphrasing for accuracy | ✓ Good |
| Semantic similarity thresholds (0.75/0.5) | Three-tier validation: auto-pass/LLM-check/auto-fail | ✓ Good |
| Composite score weights (src 0.3, korr 0.3, rel 0.2, full 0.2) | Prioritizes source grounding and correctness | ✓ Good |
| Stage-level checkpointing | Simpler than per-file, sufficient for 5-stage pipeline | ✓ Good |
| JSONL output format | HuggingFace compatible, streaming-friendly | ✓ Good |

---
*Last updated: 2026-02-19 after v5.0 milestone completion*

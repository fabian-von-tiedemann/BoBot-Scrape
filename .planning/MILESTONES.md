# Project Milestones: BoBot-Scrape

## v5.0 QA Generation Pipeline (Shipped: 2026-02-19)

**Delivered:** Complete QA generation pipeline that transforms 1,086 knowledge base documents into validated question-answer pairs for AI assistant training, with persona-driven questions, grounded answers, two-stage validation, and HuggingFace-compatible export.

**Phases completed:** 27-31 (8 plans total)

**Key accomplishments:**

- Persona-driven question generation with 5 realistic care worker personas and Gemini API
- Swedish semantic retrieval with KBLab SBERT embeddings and FAISS vector search (6,195 chunks)
- Extraction-style answer generation with inline source citations and klarspråk (B1 Swedish)
- Two-stage validation pipeline (semantic similarity + LLM-as-judge) filtering hallucinations
- HuggingFace-compatible JSONL export with full metadata per QA pair
- Resumable pipeline with stage-level checkpointing and pipeline.py --generate-qa integration

**Stats:**

- 44 files created/modified
- 2,626 lines of Python (QA pipeline)
- 5 phases, 8 plans, 23 requirements
- 9 days from start to ship (Jan 25 → Feb 2)

**Git range:** `feat(27-01)` → `docs(31)`

**What's next:** v5.1+ advanced question types, multi-document answers, analytics coverage reports

---

## v4.0 Pipeline Refactor (Shipped: 2026-01-16)

**Delivered:** Generalized ETL pipeline with unified CLI, timestamped run directories, manifest-based incremental updates, and automatic GitHub sync to bobot-kb repository.

**Phases completed:** 24-26 (3 plans total)

**Key accomplishments:**

- Unified pipeline.py CLI orchestrating all 5 ETL stages (scrape, convert, index, generate, combine) with timestamped run directories
- Manifest-based diff detection tracking document URLs and MD5 hashes between runs
- Incremental convert mode processing only new/changed documents via --include-files
- Automatic GitHub sync with --push-kb flag to push converted/, indexes/, prompts/ to bobot-kb repo
- Dry-run preview mode for safe sync operations before pushing

**Stats:**

- 8 files created/modified
- ~3,036 lines of Python (total)
- 3 phases, 3 plans, 7 tasks
- 1 day from v3.1 to v4.0

**Git range:** `feat(24-01)` → `feat(26-01)`

**What's next:** Project feature-complete. Pipeline ready for production use.

---

## v3.1 Improvements (Shipped: 2026-01-15)

**Delivered:** Parallel AI calls for faster document augmentation.

**Phases completed:** 23 (1 plan total)

**Key accomplishments:**

- Implemented asyncio/concurrent batch processing for parallel Gemini API calls
- Significantly reduced batch conversion time for large document sets

**Stats:**

- 1 phase, 1 plan
- ~3 minutes execution time

**Git range:** `feat(23-01)` → `feat(23-01)`

**What's next:** v4.0 Pipeline Refactor.

---

## v3.0 Digi Commands (Shipped: 2026-01-14)

**Delivered:** Reusable Claude commands for pushing knowledge base content to GitHub.

**Phases completed:** 22 (1 plan total)

**Key accomplishments:**

- Created /digi:push-kb command with full sync behavior (converted/, indexes/, prompts/)

**Stats:**

- 1 phase, 1 plan
- ~3 minutes execution time

**Git range:** `feat(22-01)` → `feat(22-01)`

**What's next:** v3.1 Improvements.

---

## v2.5 System Prompt Generation (Shipped: 2026-01-14)

**Delivered:** AI-powered system prompt generation pipeline — creates verksamhet-specific prompts from document metadata for AI assistant deployment.

**Phases completed:** 19-21 (3 plans total)

**Key accomplishments:**

- Built frontmatter indexer extracting metadata from 1,086 documents
- Generated 15 verksamhet-specific index files in indexes/
- Created Gemini-powered system prompt generator with Pydantic models
- Built general Swedish system prompt template with 6 sections (Identitet, Uppgift, Tonalitet, Principer, Språk, Format)
- Generated 15 combined final prompts ready for AI assistant deployment

**Stats:**

- ~1,200 lines of Python (total after v2.5)
- 3 phases, 3 plans, 6 tasks
- ~12 minutes execution time
- 45 files created/modified

**Git range:** `feat(19-01)` → `docs(21-01)`

**What's next:** Project feature-complete. All 21 phases delivered.

---

## v2.4 Knowledge Base Delivery (Shipped: 2026-01-14)

**Delivered:** Private GitHub repository with all converted markdown documents for AI assistant consumption.

**Phases completed:** 18 (1 plan total)

**Key accomplishments:**

- Created private GitHub repo fabian-von-tiedemann/bobot-kb
- Pushed 488 converted markdown documents with proper folder structure
- Created README.md documenting KB structure and frontmatter schema

**Stats:**

- 1 phase, 1 plan
- ~3 minutes execution time
- 488 files delivered

**Git range:** `feat(18-01)` → `docs(18-01)`

**What's next:** v2.5 System Prompt Generation.

---

## v2.3 Frontmatter Schema Upgrade (Shipped: 2026-01-14)

**Delivered:** Upgraded frontmatter schema with standardized category/subcategory naming and AI-extracted updated_date field.

**Phases completed:** 15-17 (3 plans total)

**Key accomplishments:**

- Renamed CSV columns from verksamhet/rutin to category/subcategory
- Added updated_date field to DocumentMetadata Pydantic model
- Updated AI prompt to extract dates (Uppdaterad, Senast ändrad, Reviderad)
- Re-converted all 1143 documents with v2.3 frontmatter schema

**Stats:**

- 3 phases, 3 plans
- ~147 minutes execution time (mostly AI extraction)
- 1143 files regenerated

**Git range:** `refactor(15-01)` → `docs(17-01)`

**What's next:** v2.4 Knowledge Base Delivery.

---

## v2.2 Frontmatter Enrichment (Shipped: 2026-01-14)

**Delivered:** Enriched markdown frontmatter with verksamhet and rutin properties — organizational hierarchy extracted from HTML DOM structure.

**Phases completed:** 11-14 (5 plans total, including 14-FIX)

**Key accomplishments:**

- Added verksamhet column to CSV export (organizational unit hierarchy)
- Added verksamhet and rutin properties to markdown frontmatter
- Implemented JavaScript DOM walker to extract subcategory headings from collapsible sections
- Filtered notification banners from rutin extraction
- Re-converted all 1143 documents with correct metadata hierarchy

**Stats:**

- 791 lines of Python (total)
- 4 phases, 5 plans
- ~2.5 hours execution time (same day)
- 2 core files modified (scrape.py, convert.py)

**Git range:** `feat(11-01)` → `fix(14-FIX)`

**What's next:** Project feature-complete. v2.2 validated via UAT.

---

## v2.1 Improvements (Shipped: 2026-01-14)

**Delivered:** Output quality improvements — URL-decoded filenames and source_url frontmatter for all 1143 converted documents.

**Phases completed:** 9-10 (2 plans total)

**Key accomplishments:**

- URL-decoded filenames in output (readable Swedish characters: ä, å, ö)
- Added source_url field to frontmatter for AI agent document referencing
- Re-converted all 1143 documents with Phase 9 improvements
- Human-readable Swedish titles in frontmatter

**Stats:**

- 554 lines of Python (src/)
- 2 phases, 2 plans, 4 tasks
- ~5 minutes execution time
- 1150 files modified (mostly re-converted markdown)

**Git range:** `feat(09-01)` → `docs(10-01)`

**What's next:** Project feature-complete. Consider maintenance or new features as needed.

---

## v2.0 Document Processing Pipeline (Shipped: 2026-01-14)

**Delivered:** Complete document processing pipeline — extracts text from PDF/DOCX, converts to structured Markdown, and generates AI metadata with Gemini.

**Phases completed:** 5-8 (4 plans total)

**Key accomplishments:**

- Text extraction from PDF documents using pymupdf
- Text extraction from Word documents using python-docx
- Markdown formatter with Swedish heading detection
- Gemini AI metadata generator (summary, keywords, topics, document_type)
- ETL pipeline CLI with batch processing and progress tracking

**Stats:**

- 822 lines of Python (total after v2.0)
- 4 phases, 4 plans
- ~21 minutes execution time

**Git range:** `feat(05-01)` → `docs(08-01)`

**What's next:** Address deferred issues in v2.1.

---

## v1.0 MVP (Shipped: 2026-01-13)

**Delivered:** Fully functional PDF/Word scraper that connects to Chrome via CDP, extracts all rutiner documents from Botkyrka kommun intranät, and downloads them to organized folders.

**Phases completed:** 1-4 (5 plans total)

**Key accomplishments:**

- Python environment with Playwright and CDP browser connection
- Chrome CDP connection script with session reuse (preserves user authentication)
- Extracted 15 rutiner category links from Botkyrka intranet using exact-match filtering
- Found 1195 documents (1067 PDFs + 128 Word files) across all categories
- Download system with CLI options (--scan-only, --download, --force)
- CSV export with URLs for assistant integration

**Stats:**

- 375 lines of Python
- 4 phases, 5 plans, ~10 tasks
- ~90 minutes from start to ship
- 21 git commits

**Git range:** `feat(01-01)` → `docs(04-01)`

**What's next:** Planning next milestone or project complete.

---

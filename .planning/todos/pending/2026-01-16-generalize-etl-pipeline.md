---
created: 2026-01-16T09:50
title: Generalize ETL pipeline with versioned output
area: pipeline
files:
  - scrape.py
  - convert.py
  - index_kb.py
  - generate_prompts.py
  - combine_prompts.py
---

## Problem

Current ETL flow outputs to fixed directories (downloaded/, converted/, indexes/, prompts/). This makes it hard to:

1. Version control different processing runs
2. Compare outputs between runs
3. Do incremental updates when new documents appear
4. Track provenance of processed data

Need a unified pipeline that:
- Creates timestamped/versioned output directories per run
- Contains all stages: /download, /convert, /index, /prompts
- Supports full re-processing and incremental updates
- Ends with push to kb-repo

Pipeline stages:
1. Capture (scrape) — download new/changed documents
2. Convert — extract text and format as markdown
3. Add metadata — frontmatter enrichment from CSV
4. AI augment — Gemini metadata generation (parallel)
5. Index — generate verksamhet indexes
6. Prompts — generate system prompts
7. Push — sync to bobot-kb repo

## Solution

TBD — needs architecture discussion:
- Directory structure for versioned runs (e.g., `runs/2026-01-16T1200/`)
- CLI interface for full vs incremental runs
- State tracking for what's been processed
- Integration with existing scripts vs new unified CLI

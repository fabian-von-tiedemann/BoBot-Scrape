# Phase 31: Export & Integration - Research

**Researched:** 2026-01-30
**Domain:** JSONL export, HuggingFace datasets compatibility, Python checkpointing, CLI integration
**Confidence:** HIGH

## Summary

This phase completes the QA generation pipeline by transforming validated QA pairs into HuggingFace-compatible JSONL format and integrating the full pipeline into the project's CLI workflow. The existing codebase already generates JSONL output from Phase 30's validation step - Phase 31 needs to transform this to strict HuggingFace format with English field names, add checkpointing for resumability, and wire into pipeline.py.

The current `qa/qa_passed.jsonl` and `qa/qa_rejected.jsonl` files use internal Swedish field names and nested validation objects. HuggingFace datasets expect flat JSONL with simple field names (`question`, `answer`, `source`). The export function will transform the existing output format to this target format.

**Primary recommendation:** Create an `export_hf()` function that transforms validated JSONL to HuggingFace format, add file-level checkpointing to handle interruptions, and integrate into pipeline.py with a `--generate-qa` flag.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| json (stdlib) | N/A | JSONL read/write | Built-in, no dependencies, streaming support |
| pathlib (stdlib) | N/A | File path handling | Already used throughout project |
| rich | 13.x | Progress tracking | Already used in validator.py |
| argparse (stdlib) | N/A | CLI argument parsing | Already used in generate_qa.py |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pydantic | 2.x | Data validation models | Already used for QA models |
| hashlib (stdlib) | N/A | Checkpoint state hashing | For detecting file changes |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| json stdlib | orjson | 3x faster but adds dependency - not needed for this data volume |
| rich progress | tqdm | Already using rich in project, consistency matters |
| pickle checkpoints | JSON checkpoints | JSON is human-readable, debuggable |

**Installation:**
No new dependencies required - all libraries already in project.

## Architecture Patterns

### Recommended Project Structure
```
src/qa/
    __init__.py          # Add export functions to exports
    exporter.py          # NEW: HuggingFace export logic
    validator.py         # Existing: JSONL output (internal format)

qa/
    qa_passed.jsonl      # Validated pairs (internal format from Phase 30)
    qa_rejected.jsonl    # Rejected pairs (internal format from Phase 30)
    qa_pairs.jsonl       # NEW: HuggingFace format export (passed only)
    qa_rejected_hf.jsonl # NEW: HuggingFace format export (rejected)
    .checkpoint.json     # NEW: Checkpoint state for resume
```

### Pattern 1: Flat JSONL for HuggingFace Datasets
**What:** One JSON object per line, flat structure, English field names
**When to use:** All HuggingFace-compatible exports
**Example:**
```json
{"question": "...", "answer": "...", "source": "...", "persona": "underskoterska/nyanstald", "validation_score": 0.85}
```

This format loads directly with:
```python
from datasets import load_dataset
dataset = load_dataset('json', data_files='qa_pairs.jsonl')
```

### Pattern 2: File-Level Checkpointing
**What:** Track processed file hashes and counts, resume from last complete file
**When to use:** Long-running batch processes that may be interrupted
**Example:**
```json
{
  "input_hash": "abc123",
  "processed_count": 150,
  "last_output_line": 149,
  "timestamp": "2026-01-30T10:00:00"
}
```

### Pattern 3: Transform Pipeline
**What:** Read internal format -> Transform fields -> Write HuggingFace format
**When to use:** Converting between different JSONL schemas
**Example:**
```python
def transform_to_hf(entry: dict) -> dict:
    """Transform internal QA format to HuggingFace format."""
    return {
        "question": entry["question"],
        "answer": entry["answer"],
        "source": entry.get("source_document", ""),
        "persona": f"{entry['persona']['roll']}/{entry['persona']['erfarenhet']}",
        "validation_score": entry["validation"]["composite_score"],
    }
```

### Anti-Patterns to Avoid
- **Nested JSON in JSONL:** HuggingFace prefers flat structures for efficiency
- **Loading entire file to memory:** Use streaming/line-by-line processing for large files
- **Checkpoint per-entry:** File-level checkpointing is simpler and sufficient for this scale
- **State in class instance:** Use explicit checkpoint file for crash recovery

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JSONL streaming | Custom file reader | `for line in file: json.loads(line)` | Standard pattern, handles encoding |
| Progress tracking | Print statements | rich.progress | Already in codebase, consistent UX |
| CLI argument parsing | Manual argv parsing | argparse | Standard, already used |
| File hashing | Custom hash logic | hashlib.md5(file.read()) | Standard, reliable |

**Key insight:** This phase is mostly glue code transforming existing outputs. The hard work (validation, scoring) is already done in Phase 30.

## Common Pitfalls

### Pitfall 1: Unicode in JSON Serialization
**What goes wrong:** Swedish characters (a, o, a) get escaped as `\u00e5` etc.
**Why it happens:** Default `json.dumps()` escapes non-ASCII
**How to avoid:** Always use `json.dumps(entry, ensure_ascii=False)`
**Warning signs:** Output file has `\u` escape sequences

### Pitfall 2: Incomplete Line on Interrupt
**What goes wrong:** Partial JSON line written if interrupted mid-write
**Why it happens:** Process killed between write() and flush()
**How to avoid:** Use temp file + atomic rename, or accept one line loss
**Warning signs:** JSON parse error on last line

### Pitfall 3: Checkpoint Stale After Code Change
**What goes wrong:** Resume produces different output than fresh run
**Why it happens:** Transform logic changed but checkpoint still valid
**How to avoid:** Include code version or logic hash in checkpoint
**Warning signs:** Inconsistent output between resumed and fresh runs

### Pitfall 4: HuggingFace Field Name Expectations
**What goes wrong:** Dataset loads but training code expects different field names
**Why it happens:** No universal standard - SQuAD uses `context`, wiki_qa uses `answer`
**How to avoid:** Use simple English names (`question`, `answer`, `source`) that match user expectations
**Warning signs:** KeyError during dataset iteration

## Code Examples

Verified patterns from official sources and existing codebase:

### JSONL Write with Unicode Support
```python
# Source: Python json module docs, existing validator.py pattern
def write_jsonl(path: Path, entries: list[dict]) -> None:
    """Write entries to JSONL file (one JSON object per line)."""
    with open(path, 'w', encoding='utf-8') as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
```

### JSONL Streaming Read
```python
# Source: Standard Python pattern
def read_jsonl_streaming(path: Path):
    """Stream JSONL entries without loading entire file."""
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
```

### HuggingFace Load Verification
```python
# Source: HuggingFace docs https://huggingface.co/docs/datasets/en/loading
from datasets import load_dataset

# Load JSONL directly
dataset = load_dataset('json', data_files='qa_pairs.jsonl')

# Verify fields
print(dataset['train'].features)  # Shows column names and types
print(dataset['train'][0])  # First example
```

### Checkpoint Save/Load Pattern
```python
# Source: Standard Python pattern for resumable processing
import json
import hashlib
from pathlib import Path

def compute_file_hash(path: Path) -> str:
    """Compute MD5 hash of file for change detection."""
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def save_checkpoint(checkpoint_path: Path, state: dict) -> None:
    """Save checkpoint atomically using temp file + rename."""
    temp_path = checkpoint_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(state, f)
    temp_path.rename(checkpoint_path)

def load_checkpoint(checkpoint_path: Path) -> dict | None:
    """Load checkpoint if exists and valid."""
    if not checkpoint_path.exists():
        return None
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
```

### Pipeline.py Integration Pattern
```python
# Source: Existing pipeline.py stage pattern
def run_stage(name: str, cmd: list[str], cwd: str = None) -> tuple[bool, float]:
    """Run a pipeline stage and capture timing."""
    # ... existing pattern from pipeline.py
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| CSV for tabular data | JSONL for streaming | 2020+ | Better for large datasets, streaming |
| `data_files=dict` | `data_files=string` | HF datasets 2.x | Simpler for single files |
| Pickle checkpoints | JSON checkpoints | Best practice | Human-readable, debuggable |

**Deprecated/outdated:**
- Using `data_type="jsonl"` - Not supported, use `"json"` even for .jsonl files

## Open Questions

Things that couldn't be fully resolved:

1. **Checkpoint granularity**
   - What we know: File-level is simplest, per-entry adds complexity
   - What's unclear: Whether user expects to resume mid-file or just mid-pipeline
   - Recommendation: Start with file-level (transform entire input files), can add per-entry later if needed

2. **Output file naming**
   - What we know: User decided English field names, HuggingFace convention
   - What's unclear: Whether to use `qa_pairs.jsonl` or `train.jsonl` as output name
   - Recommendation: Use descriptive names (`qa_pairs.jsonl`, `qa_rejected.jsonl`) matching existing pattern

3. **Whether to delete intermediate files**
   - What we know: qa_passed.jsonl (internal) vs qa_pairs.jsonl (HuggingFace) could coexist
   - What's unclear: Whether to keep both or replace
   - Recommendation: Keep both - internal format useful for debugging, HuggingFace format for export

## Sources

### Primary (HIGH confidence)
- HuggingFace datasets loading docs: https://huggingface.co/docs/datasets/en/loading
- Existing project code: `src/qa/validator.py` (JSONL write pattern)
- Existing project code: `generate_qa.py` (CLI patterns)
- Existing project code: `pipeline.py` (stage integration patterns)

### Secondary (MEDIUM confidence)
- HuggingFace forums: JSON dump format for load_dataset
- Python checkpointing patterns: https://github.com/a-rahimi/python-checkpointing

### Tertiary (LOW confidence)
- WebSearch results on checkpoint best practices (general patterns, not project-specific)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already in use in project
- Architecture: HIGH - Patterns verified against existing codebase
- Pitfalls: MEDIUM - Based on general JSONL/HuggingFace experience
- HuggingFace format: HIGH - Verified against official docs

**Research date:** 2026-01-30
**Valid until:** 30 days (stable domain, unlikely to change)

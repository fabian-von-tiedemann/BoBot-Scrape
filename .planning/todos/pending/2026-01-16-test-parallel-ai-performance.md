---
created: 2026-01-16T09:45
title: Test parallel AI performance
area: ai
files:
  - convert.py
  - src/ai/gemini.py
---

## Problem

Phase 23 implemented ThreadPoolExecutor-based batch AI metadata generation with a claimed ~10x speedup. This performance improvement has not been verified with a real conversion run against the full ~1149 document set.

Need to:
1. Run a baseline sequential conversion (or reference old timing data)
2. Run the new parallel batch conversion
3. Compare actual wall-clock times
4. Document optimal batch sizes given Gemini API rate limits

## Solution

Run `convert.py` with AI enabled on the full document set and measure:
- Total conversion time
- API calls per second achieved
- Any rate limit errors encountered
- Memory usage with different `--batch-size` values

Compare against the ~115+ seconds baseline from pre-Phase 23 implementation.

---
phase: 14-fix-hierarchy
plan: 14-FIX
type: fix
---

<objective>
Fix 1 UAT issue from Phase 14: Filter out "Pågående strömavbrott" banner from rutin extraction.

Source: 14-ISSUES.md
Priority: 0 critical, 0 major, 1 minor
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md

**Issues being fixed:**
@.planning/phases/14-fix-hierarchy/14-ISSUES.md

**Original plan for reference:**
@.planning/phases/14-fix-hierarchy/14-01-PLAN.md

**Source file:**
@scrape.py
</context>

<tasks>
<task type="auto">
  <name>Task 1: Filter notification banners from rutin extraction</name>
  <files>scrape.py</files>
  <action>
Update the JavaScript DOM walker (lines 222-281) to filter out known notification/banner headings.

Add a blocklist of headings that should be ignored:
- "Pågående strömavbrott" (current outage notification)
- Any other obvious notification patterns

Modify the heading extraction logic:
1. After finding a heading, check if it's in the blocklist
2. If blocklisted, continue searching for the next preceding heading
3. If no valid heading found, leave rutin empty (same as current fallback)

This is a minimal fix - just skip known bad headings rather than rewriting the DOM traversal logic.
  </action>
  <verify>
Run: `grep "Pågående strömavbrott" downloads/documents.csv | wc -l`
Expected: 0 (no documents should have this as rutin)
  </verify>
  <done>
The scraper no longer picks up "Pågående strömavbrott" as a rutin value.
  </done>
</task>

<task type="auto">
  <name>Task 2: Re-run scraper to update CSV</name>
  <files>downloads/documents.csv</files>
  <action>
Run the scraper in scan-only mode to regenerate documents.csv with the fix:

```bash
.venv/bin/python scrape.py --scan-only
```

Note: This requires an active Chrome session connected to the intranet. If not available, this task becomes a checkpoint for manual execution.
  </action>
  <verify>
Run: `grep "Pågående strömavbrott" downloads/documents.csv | wc -l`
Expected: 0
  </verify>
  <done>
documents.csv updated with no "Pågående strömavbrott" entries in rutin column.
  </done>
</task>

<task type="auto">
  <name>Task 3: Re-convert affected documents</name>
  <files>converted/**/*.md</files>
  <action>
Re-convert the ~54 affected documents to update their frontmatter with correct (or empty) rutin values.

```bash
.venv/bin/python convert.py --skip-ai
```

This will re-convert all documents using the updated CSV metadata.
  </action>
  <verify>
Spot check a previously affected document:
- Bemanningsenheten/Anmäla frånvaro för timvikarier BE.md
- Should NOT have rutin: "Pågående strömavbrott"
  </verify>
  <done>
All affected markdown files updated with correct rutin values (or empty if no valid heading found).
  </done>
</task>
</tasks>

<verification>
Before declaring plan complete:
- [ ] No documents in CSV have "Pågående strömavbrott" as rutin
- [ ] No markdown files in converted/ have rutin: "Pågående strömavbrott" in frontmatter
- [ ] Total document count unchanged (~1143)
</verification>

<success_criteria>
- UAT-001 from 14-ISSUES.md addressed
- 54 affected documents now have correct (or empty) rutin
- Ready for re-verification with /gsd:verify-work
</success_criteria>

<output>
After completion, create `.planning/phases/14-fix-hierarchy/14-FIX-SUMMARY.md`
</output>

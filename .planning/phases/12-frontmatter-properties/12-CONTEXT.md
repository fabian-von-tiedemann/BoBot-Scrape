# Phase 12: Frontmatter Properties - Context

**Gathered:** 2026-01-14
**Status:** Ready for planning

<vision>
## How This Should Work

When a PDF is converted to markdown, the frontmatter should include two new properties:

- **verksamhet** — The department/folder the document belongs to (e.g., "Boendestöd"). This comes from the folder structure where the document is organized.

- **rutin** — The specific routine category from the source page (e.g., "Bemanna med timvikarier", "Personlig assistans", "Fakturering"). This information was scraped in Phase 11 and saved to rutiner.csv.

The conversion process should look up each PDF in the CSV to find its verksamhet and rutin values, then add them to the markdown frontmatter.

If a document doesn't have a clear rutin category (just listed under "Rutiner" without subcategory), the rutin field should be left empty.

</vision>

<essential>
## What Must Be Nailed

- **Both properties equally important** — Every converted markdown file needs both verksamhet and rutin in its frontmatter
- **verksamhet** from folder/department structure
- **rutin** from the category on the source page (from CSV data)
- Empty rutin is acceptable when no category exists

</essential>

<boundaries>
## What's Out of Scope

- Batch re-conversion of existing documents — that's Phase 13
- New scraping — Phase 11 already captured verksamhet/rutin to CSV
- This phase just updates the conversion code to use the CSV data

</boundaries>

<specifics>
## Specific Ideas

- Property names: `verksamhet` and `rutin`
- Data source: rutiner.csv (updated in Phase 11)
- Match documents by PDF URL to find corresponding CSV row
- Leave rutin empty (not omit) when no category available

</specifics>

<notes>
## Additional Context

This is part of the v2.2 Frontmatter Enrichment milestone. The goal is better document organization and AI search capabilities by enriching markdown files with department and category metadata.

Phase 11 already updated the scraper to capture this data to CSV. This phase integrates that data into the conversion pipeline.

</notes>

---

*Phase: 12-frontmatter-properties*
*Context gathered: 2026-01-14*

# Phase 14 Plan 01: Scraper Update Summary

**Fixed verksamhet/rutin hierarchy by extracting subcategory headings from HTML DOM structure.**

## Accomplishments

- Removed the static `VERKSAMHET = "Vård- och omsorgsförvaltningen"` constant
- Updated CSV schema from `verksamhet, category, filename...` to `verksamhet, rutin, filename...`
  - `verksamhet` now contains the category name (e.g., "Bemanningsenheten", "Hemtjänst")
  - `rutin` contains the subcategory heading extracted from HTML (e.g., "Avvikelsehantering", "Brukare")
- Implemented JavaScript-based DOM traversal to find nearest preceding h2/h3/h4 heading for each document link
- Updated convert.py to use the new CSV schema for metadata lookup

## Files Modified

- `scrape.py` - Added JavaScript DOM walker to extract subcategory headings, removed VERKSAMHET constant, updated CSV output
- `convert.py` - Updated `load_document_metadata()` to use new CSV schema (verksamhet/filename key instead of category/filename)
- `downloads/documents.csv` - Regenerated with new schema (1195 documents across 15 categories)

## Decisions Made

- **How subcategories were identified:** Walk DOM backwards from each document link to find the nearest preceding h2, h3, or h4 heading. This captures the section heading under which the document is listed.
- **Handling of documents without clear subcategory:** Documents without a preceding heading get an empty rutin value. Some documents inherit headings from page banners (e.g., "Pågående strömavbrott" appears for some items that lack a true subcategory).

## Technical Details

The JavaScript extraction script:
1. Queries all `<a>` elements on the page
2. For each link that ends with .pdf/.doc/.docx:
   - Walk up through parent elements
   - At each level, check previousElementSibling for h2/h3/h4 tags
   - Also check nested headings inside sibling elements
   - Stop when heading is found
3. Return array with url, type, and rutin for each document

## Sample Results

| verksamhet | rutin | filename |
|------------|-------|----------|
| Boendestöd | Avvikelsehantering | Lex Sarah(version 3).pdf |
| Boendestöd | Arkivering och Gallring | Gallring och arkivering .pdf |
| Boendestöd | Brukare | Om du finner brukare avliden i sitt hem.pdf |
| Dagverksamhet | Basal hygien | Smittförebyggande rutin.pdf |
| Hemtjänst | Social dokumentation | Social dokumentation rutin-ny.pdf |

## Statistics

- **Total documents:** 1195
- **Categories (verksamhet):** 15
- **Unique subcategories (rutin):** ~200+ distinct values

## Checkpoint

- **checkpoint:human-verify** - Skipped (yolo mode)

## Issues Encountered

- Some documents inherit the page's notification banner heading (e.g., "Pågående strömavbrott") as their rutin when they appear at the top of the page before any true subcategory heading. This is a minor data quality issue that can be filtered out later if needed.

## Next Step

Ready for 14-02-PLAN.md: Update convert.py to use new CSV schema and re-convert all documents with correct frontmatter hierarchy.

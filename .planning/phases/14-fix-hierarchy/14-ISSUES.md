# UAT Issues: Phase 14

**Tested:** 2026-01-14
**Source:** .planning/phases/14-fix-hierarchy/14-01-SUMMARY.md, 14-02-SUMMARY.md
**Tester:** User via /gsd:verify-work

## Open Issues

[None]

## Resolved Issues

### UAT-001: "Pågående strömavbrott" felaktigt som rutin för 54 dokument

**Discovered:** 2026-01-14
**Resolved:** 2026-01-14 - Fixed in 14-FIX.md
**Phase/Plan:** 14-01
**Severity:** Minor
**Feature:** Subcategory (rutin) extraction from HTML DOM
**Description:** 54 dokument (ca 4.5%) har "Pågående strömavbrott" som rutin-värde istället för den korrekta underkategorin. Detta verkar vara en notis-banner på webbsidan som felaktigt plockas upp av DOM-traverseringen.
**Resolution:** Added blocklist to JavaScript DOM walker in scrape.py to filter out notification banner headings ("pågående strömavbrott", "driftstörning", "meddelande", "notis"). Re-scraped and re-converted all 1145 documents.

---

*Phase: 14-fix-hierarchy*
*Tested: 2026-01-14*

# BoBot-Scrape

## What This Is

En PDF-scraper som automatiserar nedladdning av rutindokument från Botkyrka kommuns intranät (BoTwebb). Använder användarens befintliga Chrome-session för att hantera SAML-autentisering och laddar ner alla PDF:er organiserade i mappar baserat på länkstrukturen.

## Core Value

Alla PDF:er nedladdade — ingen PDF ska missas, oavsett hur sidstrukturen ser ut.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Ansluta till befintlig Chrome-session med aktiv inloggning
- [ ] Navigera till startsidan och extrahera alla kategorilänkar
- [ ] Följa varje kategorilänk och hitta alla PDF-länkar
- [ ] Ladda ner varje PDF till rätt kategorimapp
- [ ] Skapa mappstruktur baserad på kategorilänkarnas namn

### Out of Scope

- Inkrementella uppdateringar (bara ladda ner nya/ändrade) — håll v1 enkel
- Metadata-hantering (versioner, nedladdningstider) — onödig komplexitet
- GUI/grafiskt gränssnitt — CLI-skript räcker
- Felåterhämtning vid nätverksfel — kan läggas till senare
- Parallell nedladdning — enkelhet prioriteras

## Context

**Källa:** https://botwebb.botkyrka.se/sidor/din-forvaltning/forvaltningar/vard--och-omsorgsforvaltningen/kvalitet/lagar-termer-och-styrdokument/styrdokument/rutiner-for-utforare.html

**Sidstruktur (förväntad):**
1. Startsidan innehåller en lista med länkar till kategorisidor
2. Varje kategorisida innehåller länkar till PDF-dokument
3. PDF:erna är rutindokument för Vård- och omsorgsförvaltningen

**Autentisering:**
- Sidan kräver SAML-inloggning (kommunal SSO)
- Användaren är redan inloggad via sin vanliga Chrome-webbläsare
- Scriptet ska använda befintlig Chrome-profil för att ärva sessionen

**Teknisk approach:**
- Playwright med `connect_over_cdp` för att ansluta till körande Chrome
- Chrome måste startas med remote debugging aktiverat
- Python för enkel scripting

## Constraints

- **Webbläsare**: Chrome (användarens befintliga profil med aktiv session)
- **Autentisering**: Måste använda befintlig session — ingen inloggningsautomatisering

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Playwright över Selenium | Bättre CDP-stöd för att ansluta till körande Chrome | — Pending |
| Python som språk | Enkelt, Playwright har bra Python-stöd | — Pending |
| Två-nivå-traversering | Startsida → kategorisidor → PDF:er | — Pending |

---
*Last updated: 2026-01-13 after initialization*

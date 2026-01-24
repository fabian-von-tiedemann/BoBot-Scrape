# Requirements: BoBot-Scrape v5.0 QA Generation Pipeline

**Defined:** 2026-01-24
**Core Value:** Generera tusentals validerade QA-par från kunskapsbasen för AI-assistentträning

## v5.0 Requirements

Requirements for QA generation pipeline. Each maps to roadmap phases.

### Persona Model

- [ ] **PERS-01**: Definiera persona-modell med roll + situation
- [ ] **PERS-02**: Skapa 5-10 distinkta personas (undersköterska, hemtjänst, nattjour, ny på jobbet, etc)
- [ ] **PERS-03**: Persona-konfiguration i YAML-fil

### Question Generation

- [ ] **QGEN-01**: Generera frågor från dokumentinnehåll med Gemini
- [ ] **QGEN-02**: Persona-drivna frågor (formulerade som persona skulle fråga)
- [ ] **QGEN-03**: Källdokumentreferens för varje fråga
- [ ] **QGEN-04**: 3-5 frågor per dokument
- [ ] **QGEN-05**: Batch-generering med progress-tracking

### Answer Generation

- [ ] **AGEN-01**: Svar grundade i källdokument
- [ ] **AGEN-02**: Källcitat i varje svar (dokumentnamn, sektion)
- [ ] **AGEN-03**: Klarspråk (enkel svenska, B1-nivå)
- [ ] **AGEN-04**: Extraktionsstil (citera relevant text från källa)

### Validation

- [ ] **VALD-01**: Källverifiering (svar finns i refererat dokument)
- [ ] **VALD-02**: Kvalitetsbedömning (relevans, korrekthet, fullständighet)
- [ ] **VALD-03**: Tvåstegs validering med LLM-as-judge
- [ ] **VALD-04**: Filtrera bort hallucineringar och låg kvalitet
- [ ] **VALD-05**: Validerings-score i output (för granskning)

### Export

- [ ] **EXPRT-01**: JSONL-export (HuggingFace-kompatibelt)
- [ ] **EXPRT-02**: Metadata per QA-par (persona, källa, score)
- [ ] **EXPRT-03**: Separat fil för godkända vs underkända QA-par

### Integration

- [ ] **INTG-01**: Standalone CLI (generate_qa.py)
- [ ] **INTG-02**: Integration i pipeline.py som valfritt steg
- [ ] **INTG-03**: Checkpointing för resume vid avbrott

## v5.1+ Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Question Types

- **QTYP-01**: Scenario-baserade frågor ("Vad gör du om...")
- **QTYP-02**: Felsökningsfrågor ("Varför fungerar inte...")
- **QTYP-03**: Jämförande frågor ("Skillnad mellan X och Y")

### Advanced Answer Features

- **AFEAT-01**: Adaptivt svarsformat (kort/stegvis baserat på frågetyp)
- **AFEAT-02**: Multi-dokument-svar (kombinera info från flera källor)

### Analytics

- **ANLYT-01**: Coverage-rapport (hur många dokument har QA-par)
- **ANLYT-02**: Kvalitetsfördelning (score-histogram)
- **ANLYT-03**: Persona-fördelning (balanserad representation)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fine-tuning data format | Använder QA för prompt-kontext och eval, inte fine-tuning |
| Human-in-the-loop UI | CLI är tillräckligt för denna milestone |
| Real-time generation | Batch-process räcker |
| Embedding database | numpy i minnet räcker för 1100 dokument |
| Gold standard dataset | Kräver domänexpertis utanför scope |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PERS-01 | Phase 27 | Pending |
| PERS-02 | Phase 27 | Pending |
| PERS-03 | Phase 27 | Pending |
| QGEN-01 | Phase 28 | Pending |
| QGEN-02 | Phase 28 | Pending |
| QGEN-03 | Phase 28 | Pending |
| QGEN-04 | Phase 28 | Pending |
| QGEN-05 | Phase 28 | Pending |
| AGEN-01 | Phase 29 | Pending |
| AGEN-02 | Phase 29 | Pending |
| AGEN-03 | Phase 29 | Pending |
| AGEN-04 | Phase 29 | Pending |
| VALD-01 | Phase 30 | Pending |
| VALD-02 | Phase 30 | Pending |
| VALD-03 | Phase 30 | Pending |
| VALD-04 | Phase 30 | Pending |
| VALD-05 | Phase 30 | Pending |
| EXPRT-01 | Phase 31 | Pending |
| EXPRT-02 | Phase 31 | Pending |
| EXPRT-03 | Phase 31 | Pending |
| INTG-01 | Phase 31 | Pending |
| INTG-02 | Phase 31 | Pending |
| INTG-03 | Phase 31 | Pending |

**Coverage:**

- v5.0 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-24*
*Last updated: 2026-01-24 after initial definition*

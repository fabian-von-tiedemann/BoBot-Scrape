# Requirements: BoBot-Scrape v5.0 QA Generation Pipeline

**Defined:** 2026-01-24
**Core Value:** Generera tusentals validerade QA-par fran kunskapsbasen for AI-assistenttraning

## v5.0 Requirements

Requirements for QA generation pipeline. Each maps to roadmap phases.

### Persona Model

- [x] **PERS-01**: Definiera persona-modell med roll + situation
- [x] **PERS-02**: Skapa 5-10 distinkta personas (underskoterska, hemtjanst, nattjour, ny pa jobbet, etc)
- [x] **PERS-03**: Persona-konfiguration i YAML-fil

### Question Generation

- [ ] **QGEN-01**: Generera fragor fran dokumentinnehall med Gemini
- [ ] **QGEN-02**: Persona-drivna fragor (formulerade som persona skulle fraga)
- [ ] **QGEN-03**: Kalldokumentreferens for varje fraga
- [ ] **QGEN-04**: 3-5 fragor per dokument
- [ ] **QGEN-05**: Batch-generering med progress-tracking

### Answer Generation

- [ ] **AGEN-01**: Svar grundade i kalldokument
- [ ] **AGEN-02**: Kallcitat i varje svar (dokumentnamn, sektion)
- [ ] **AGEN-03**: Klarsprak (enkel svenska, B1-niva)
- [ ] **AGEN-04**: Extraktionsstil (citera relevant text fran kalla)

### Validation

- [ ] **VALD-01**: Kallverifiering (svar finns i refererat dokument)
- [ ] **VALD-02**: Kvalitetsbedomning (relevans, korrekthet, fullstandighet)
- [ ] **VALD-03**: Tvastegs validering med LLM-as-judge
- [ ] **VALD-04**: Filtrera bort hallucineringar och lag kvalitet
- [ ] **VALD-05**: Validerings-score i output (for granskning)

### Export

- [ ] **EXPRT-01**: JSONL-export (HuggingFace-kompatibelt)
- [ ] **EXPRT-02**: Metadata per QA-par (persona, kalla, score)
- [ ] **EXPRT-03**: Separat fil for godkanda vs underkanda QA-par

### Integration

- [ ] **INTG-01**: Standalone CLI (generate_qa.py)
- [ ] **INTG-02**: Integration i pipeline.py som valfritt steg
- [ ] **INTG-03**: Checkpointing for resume vid avbrott

## v5.1+ Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Question Types

- **QTYP-01**: Scenario-baserade fragor ("Vad gor du om...")
- **QTYP-02**: Felsokningsfragor ("Varfor fungerar inte...")
- **QTYP-03**: Jamforande fragor ("Skillnad mellan X och Y")

### Advanced Answer Features

- **AFEAT-01**: Adaptivt svarsformat (kort/stegvis baserat pa fragetyp)
- **AFEAT-02**: Multi-dokument-svar (kombinera info fran flera kallor)

### Analytics

- **ANLYT-01**: Coverage-rapport (hur manga dokument har QA-par)
- **ANLYT-02**: Kvalitetsfordelning (score-histogram)
- **ANLYT-03**: Persona-fordelning (balanserad representation)

## Out of Scope

| Feature                  | Reason                                                       |
|--------------------------|--------------------------------------------------------------|
| Fine-tuning data format  | Anvander QA for prompt-kontext och eval, inte fine-tuning    |
| Human-in-the-loop UI     | CLI ar tillrackligt for denna milestone                      |
| Real-time generation     | Batch-process racker                                         |
| Embedding database       | numpy i minnet racker for 1100 dokument                      |
| Gold standard dataset    | Kraver domanexpertis utanfor scope                           |

## Traceability

| Requirement | Phase    | Status  |
|-------------|----------|---------|
| PERS-01     | Phase 27 | Complete |
| PERS-02     | Phase 27 | Complete |
| PERS-03     | Phase 27 | Complete |
| QGEN-01     | Phase 28 | Pending |
| QGEN-02     | Phase 28 | Pending |
| QGEN-03     | Phase 28 | Pending |
| QGEN-04     | Phase 28 | Pending |
| QGEN-05     | Phase 28 | Pending |
| AGEN-01     | Phase 29 | Pending |
| AGEN-02     | Phase 29 | Pending |
| AGEN-03     | Phase 29 | Pending |
| AGEN-04     | Phase 29 | Pending |
| VALD-01     | Phase 30 | Pending |
| VALD-02     | Phase 30 | Pending |
| VALD-03     | Phase 30 | Pending |
| VALD-04     | Phase 30 | Pending |
| VALD-05     | Phase 30 | Pending |
| EXPRT-01    | Phase 31 | Pending |
| EXPRT-02    | Phase 31 | Pending |
| EXPRT-03    | Phase 31 | Pending |
| INTG-01     | Phase 31 | Pending |
| INTG-02     | Phase 31 | Pending |
| INTG-03     | Phase 31 | Pending |

**Coverage:**

- v5.0 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-01-24*
*Last updated: 2026-01-24 after roadmap creation*

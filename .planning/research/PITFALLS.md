# Pitfalls Research: QA Generation Pipeline

**Project:** BoBot-Scrape QA Generation (v5.0)
**Domain:** Swedish municipal care worker procedure documents
**Researched:** 2026-01-24
**Confidence:** MEDIUM (WebSearch-verified with domain reasoning)

---

## Quality Pitfalls

### P1: Hallucinated Procedure Steps

**What goes wrong:** LLM invents steps, phone numbers, or contacts that do not exist in the source document. For care workers following these procedures in emergencies, fabricated information could cause harm.

**Why it happens:**
- LLMs trained on general Swedish content may "fill in" expected procedure patterns
- Swedish municipal terminology is underrepresented in training data
- Model confidence is high even when generating unsupported content

**Warning signs:**
- Answers contain specific numbers (phone, room numbers) not in source
- Procedures have more steps than the original document
- Generic "best practice" language appears instead of document-specific guidance

**Prevention strategy:**
- Require strict grounding: Every answer must cite exact text from source
- Include source document snippet in QA pair for verification
- Use extraction-style prompts ("What does the document say about X?") not generation-style ("How should one handle X?")
- Implement post-generation verification comparing answer tokens to source

**Phase to address:** QA Generation phase (core prompt design)

---

### P2: Wrong Source Attribution

**What goes wrong:** QA pair cites wrong document or mixes information from multiple documents. User trusts answer but follows outdated or inapplicable procedure.

**Why it happens:**
- Batch processing without proper document isolation
- Context window includes multiple documents
- Similar document names (e.g., "Hot och vald - rutin" vs "Hot och vald - policy")

**Warning signs:**
- Metadata references differ from document being processed
- Cross-references to procedures not in the source document
- Category/subcategory mismatches

**Prevention strategy:**
- Process one document at a time with full context
- Include document metadata (filename, category) in generation prompt
- Validate source_file field matches actual processing target
- Store document hash with QA pair for lineage tracking

**Phase to address:** Pipeline design phase

---

### P3: Overly Specific Questions

**What goes wrong:** Generated questions are too narrow, matching only exact document phrasing. Real users ask questions differently, so QA pairs become useless for evaluation.

**Why it happens:**
- Conditioning LLM on specific text chunks produces extractive questions
- Questions mirror document structure rather than user intent
- No variation in question phrasing

**Warning signs:**
- Questions contain rare terminology only found in source
- Questions are answerable only by exact phrase matching
- 90%+ of questions are "What does the document say about..."

**Prevention strategy:**
- Generate multiple question phrasings per answer
- Include user personas in prompts (second-language speaker, stressed mobile worker)
- Create questions at multiple difficulty levels (factoid, procedural, reasoning)
- Validate questions are answerable without seeing the exact source passage

**Phase to address:** QA Generation phase (prompt engineering)

**Source:** [Ragas synthetic data generation guide](https://blog.ragas.io/all-about-synthetic-data-generation)

---

### P4: Missing Critical Safety Information

**What goes wrong:** QA pairs cover routine content but miss safety-critical procedures. Evaluation dataset underrepresents high-stakes scenarios.

**Why it happens:**
- Safety information often in specific sections (e.g., "Hotfulla situationer")
- Uniform sampling misses concentrated critical content
- LLM may skip "obvious" safety content as less interesting

**Warning signs:**
- Few QA pairs about emergency procedures
- Risk-related keywords (nod, larma, 112) underrepresented
- Categories like "Hot och vald" have fewer QA pairs than simpler topics

**Prevention strategy:**
- Tag documents by safety-criticality during preprocessing
- Weight generation toward safety-tagged sections
- Require minimum QA pair count for safety categories
- Manual review sample from each high-stakes document

**Phase to address:** Document tagging phase + QA Generation phase

---

## Language Pitfalls

### L1: Swedish Language Model Gaps

**What goes wrong:** LLM misunderstands Swedish compound words, domain terms, or produces unnatural Swedish phrasing. Care workers find answers confusing.

**Why it happens:**
- Most LLMs trained primarily on English
- Swedish care/municipal terminology underrepresented
- Compound word semantics differ from English patterns

**Warning signs:**
- Compound words split incorrectly ("arbets miljoverket" instead of "Arbetsmiljoverket")
- Formal vs informal register mismatch
- Loan words or English patterns in Swedish answers

**Prevention strategy:**
- Use models with strong Swedish performance (GPT-4, Claude 3.5 evaluated on Swedish Medical LLM Benchmark)
- Include Swedish terminology glossary in system prompt
- Validate outputs against Swedish spell-check
- Sample review by native Swedish speaker

**Phase to address:** Model selection phase + QA Generation phase

**Source:** [Swedish Medical LLM Benchmark (SMLB)](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full)

---

### L2: Second-Language Speaker Accessibility

**What goes wrong:** Generated answers use complex Swedish that second-language speakers struggle to understand. Target users cannot use the assistant effectively.

**Why it happens:**
- LLM defaults to formal, complex Swedish (myndighetssprak)
- Source documents may already be complex
- No accessibility requirements in generation prompt

**Warning signs:**
- Answers contain long sentences (>25 words)
- Passive voice dominates
- Domain jargon without explanation
- Subordinate clauses nested deeply

**Prevention strategy:**
- Include klarsprak (plain Swedish) guidelines in generation prompt
- Target CEFR B1 reading level for answers
- Measure readability (LIX score) on generated answers
- Prefer active voice, short sentences, common vocabulary
- Add glossary explanations for necessary technical terms

**Phase to address:** QA Generation phase (answer style guidelines)

**Source:** [Plain Swedish Language Initiative](https://www.isof.se/other-languages/english/plain-swedish-language)

---

### L3: Inconsistent Terminology

**What goes wrong:** Same concept called different names across QA pairs. Users search for one term, system retrieves another.

**Why it happens:**
- Source documents use varying terminology
- LLM paraphrases inconsistently
- No canonical vocabulary enforced

**Warning signs:**
- "KIA-anmalan" vs "tillbudsrapport" vs "avvikelseanmalan" used interchangeably
- Role names vary ("enhetschef" vs "chef" vs "ansvarig")
- Process names inconsistent

**Prevention strategy:**
- Create terminology mapping from source documents
- Include preferred terms in system prompt
- Post-process to normalize key terms
- Build synonym list for retrieval

**Phase to address:** Preprocessing phase + QA Generation phase

---

## Scale Pitfalls

### S1: API Cost Explosion

**What goes wrong:** Generating 1000s of QA pairs from 1100 documents costs more than budgeted. Project stalls or quality compromises made.

**Why it happens:**
- Underestimating tokens per document (avg 2-4 pages)
- Multiple generation passes (questions, answers, variations)
- Re-runs due to quality issues

**Warning signs:**
- Early batches exceed cost projections
- Quality prompts require more tokens than expected
- Validation failures require regeneration

**Prevention strategy:**
- Calculate expected tokens before starting (1100 docs x ~2000 tokens x QA multiplier)
- Use batch API for 50% discount (OpenAI/Anthropic)
- Start with smaller model (Haiku/Gemini Flash) for first pass
- Implement caching for repeated context
- Budget 30% buffer for reruns

**Estimated costs (rough):**
- ~1100 docs x 2000 tokens input = 2.2M input tokens
- ~10 QA pairs/doc x 200 tokens output = 2.2M output tokens
- With Claude Haiku: ~$1.10 input + $5.50 output = ~$7 total
- With Claude Sonnet: ~$6.60 input + $33 output = ~$40 total
- Add 3x for multiple passes: $20-120 range

**Phase to address:** Planning phase (budget) + Pipeline design phase

**Source:** [Anthropic API pricing](https://www.finout.io/blog/anthropic-api-pricing)

---

### S2: Rate Limit Blocking

**What goes wrong:** Batch processing hits rate limits, causing timeouts, partial results, or corrupted output state.

**Why it happens:**
- Default rate limits restrictive (5 RPM for some tiers)
- No exponential backoff implemented
- Processing state not persisted between runs

**Warning signs:**
- 429 errors in logs
- Incomplete batch runs
- Resuming creates duplicate QA pairs

**Prevention strategy:**
- Implement exponential backoff with jitter
- Use batch API (async, higher limits)
- Persist processing state (which docs completed)
- Add checkpointing every N documents
- Request limit increases if needed

**Phase to address:** Pipeline design phase

**Source:** [Anthropic rate limits documentation](https://docs.anthropic.com/en/api/rate-limits)

---

### S3: Processing Time Underestimation

**What goes wrong:** Full pipeline takes days instead of hours. Development iteration becomes painfully slow.

**Why it happens:**
- API latency ~2-5s per request
- Sequential processing of 1100 documents
- No parallelization
- Retry overhead

**Warning signs:**
- Single document processing >10 seconds
- Estimated total time >8 hours
- Cannot iterate on prompt design quickly

**Prevention strategy:**
- Implement concurrent processing (5-10 parallel requests)
- Use batch API for bulk processing
- Create small test set (10-20 docs) for prompt iteration
- Separate generation from validation for faster feedback
- Profile and optimize slowest steps

**Phase to address:** Pipeline design phase

---

## Domain Pitfalls

### D1: Outdated Procedure References

**What goes wrong:** QA pairs reference procedures that have been updated. Answer contradicts current practice.

**Why it happens:**
- Source documents from different time periods
- No version tracking in current system
- Documents may reference superseded procedures

**Warning signs:**
- Dates in documents span multiple years
- References to "ny rutin" or "uppdaterad" not captured
- Conflicting answers about same procedure

**Prevention strategy:**
- Extract and track document dates (already in frontmatter: updated_date)
- Flag documents older than 1 year for review
- Prioritize recent documents when conflicts exist
- Include document date in QA pair metadata
- Build update detection comparing document versions

**Phase to address:** Document preprocessing phase

---

### D2: Role/Responsibility Confusion

**What goes wrong:** QA pairs mix up who is responsible for what. Care worker does wrong task or skips necessary escalation.

**Why it happens:**
- Documents have complex role hierarchies (enhetschef, medarbetare, skyddsombud)
- LLM conflates similar-sounding responsibilities
- Questions don't specify which role is asking

**Warning signs:**
- "You should" answers without specifying which role
- Escalation paths unclear
- Management responsibilities assigned to care workers

**Prevention strategy:**
- Require explicit role specification in questions
- Include "Roller och ansvar" section context
- Generate role-specific QA pairs (e.g., "As a medarbetare, what should I do when...")
- Validate answers against role-specific content

**Phase to address:** QA Generation phase (prompt design)

---

### D3: Cross-Document Dependencies

**What goes wrong:** Document references another procedure that user needs but QA pair doesn't surface. Partial information more dangerous than no information.

**Why it happens:**
- Swedish rutindokument frequently reference each other
- "Se aven rutin X" not captured as dependency
- Questions answered from single document context

**Warning signs:**
- Answers contain "enligt rutin" without specifying which
- References to "genomforandeplan" without context
- Missing procedural prerequisites

**Prevention strategy:**
- Parse document cross-references during preprocessing
- Store reference graph between documents
- Include referenced document summaries in context
- Flag answers that depend on external documents

**Phase to address:** Document analysis phase + QA Generation phase

---

### D4: Municipal-Specific Context Loss

**What goes wrong:** QA pairs lose Botkyrka kommun-specific information. Answers become generic Swedish care guidance.

**Why it happens:**
- LLM generalizes from training data
- Municipal variations not emphasized
- System-specific terms (KIA, BE-jouren) not explained

**Warning signs:**
- Answers could apply to any Swedish municipality
- Local phone numbers/contacts replaced with generic guidance
- Botkyrka-specific systems not mentioned

**Prevention strategy:**
- Include municipal context in system prompt
- Preserve specific names, numbers, systems
- Validate Botkyrka-specific terms appear in outputs
- Flag generic answers for review

**Phase to address:** QA Generation phase (system prompt)

---

## Validation Pitfalls

### V1: LLM-as-Judge Bias

**What goes wrong:** Using same LLM family to generate and validate creates systematic blind spots. Bad QA pairs pass validation.

**Why it happens:**
- LLMs exhibit self-preference bias
- Same failure modes in generation and validation
- Hallucinations look plausible to same model family

**Warning signs:**
- Very high validation pass rates (>95%)
- Human review finds issues validation missed
- Validation agrees with obviously wrong answers

**Prevention strategy:**
- Use different model for validation (if using Claude for generation, use GPT for validation)
- Include human review sample (5-10%)
- Create adversarial test cases with known-wrong answers
- Weight validation toward source-grounding, not plausibility

**Phase to address:** Validation phase

**Source:** [LLM evaluation pitfalls](https://www.honeyhive.ai/post/avoiding-common-pitfalls-in-llm-evaluation)

---

### V2: Ground Truth Absence

**What goes wrong:** No gold standard to measure against. Cannot tell if QA quality is improving.

**Why it happens:**
- Synthetic data has no human-verified baseline
- Creating ground truth is expensive
- Evaluation metrics unclear

**Warning signs:**
- No way to compute precision/recall
- Quality discussions are subjective
- Cannot compare prompt variations quantitatively

**Prevention strategy:**
- Create small human-annotated gold set (50-100 QA pairs)
- Sample across categories and difficulty levels
- Use domain expert (care worker or manager) for annotation
- Compute metrics against gold set for each pipeline version

**Phase to address:** Validation phase (early investment)

---

### V3: Validation Only Catches Obvious Errors

**What goes wrong:** Validation catches format issues but misses subtle semantic errors. False sense of quality.

**Why it happens:**
- Structural validation (JSON format, field presence) is easy
- Semantic validation (answer correctness) is hard
- Time pressure favors automated checks

**Warning signs:**
- Validation = "did it parse correctly?"
- No source comparison in validation
- High pass rate, low downstream performance

**Prevention strategy:**
- Implement multi-level validation:
  1. Structural: JSON parses, required fields present
  2. Grounding: Answer tokens appear in source
  3. Semantic: Answer correctly addresses question
  4. Completeness: Safety-critical info not omitted
- Weight toward grounding and semantic checks

**Phase to address:** Validation phase

---

### V4: Insufficient Diversity Validation

**What goes wrong:** QA pairs cluster around easy topics. Dataset appears large but covers narrow slice of domain.

**Why it happens:**
- Some documents generate more QA pairs than others
- Easy questions overrepresented
- No category balancing

**Warning signs:**
- Topic distribution skewed
- 80% of QA pairs from 20% of categories
- Question types imbalanced (all factoid, no procedural)

**Prevention strategy:**
- Track distribution by category, subcategory, document
- Set minimum coverage thresholds per category
- Classify question types and balance
- Report diversity metrics alongside quantity

**Phase to address:** Validation phase + Reporting

---

## Export/Usage Pitfalls

### E1: Format Incompatibility

**What goes wrong:** QA pairs exported in format that downstream system cannot consume. Manual reformatting required.

**Why it happens:**
- Unclear downstream requirements
- Format changes during development
- Multiple consumers with different needs

**Warning signs:**
- Field names don't match downstream schema
- Encoding issues (UTF-8 Swedish characters)
- Nested structure not supported

**Prevention strategy:**
- Define target schema upfront with downstream team
- Validate export against schema before handoff
- Support multiple export formats (JSON, CSV, JSONL)
- Include encoding and character tests in validation

**Phase to address:** Export phase (design early)

---

### E2: Missing Traceability

**What goes wrong:** QA pair cannot be traced back to source document. Cannot update when source changes, cannot debug quality issues.

**Why it happens:**
- Traceability seen as overhead
- ID generation not systematic
- Links broken during processing

**Warning signs:**
- "Where did this answer come from?" unanswerable
- Source document updates don't propagate
- Quality issues cannot be attributed

**Prevention strategy:**
- Include in every QA pair:
  - source_file (document path)
  - source_hash (content fingerprint)
  - generation_date
  - model_version
  - prompt_version
- Store generation parameters for reproducibility

**Phase to address:** Pipeline design phase (early)

---

### E3: Stale QA Pairs in Production

**What goes wrong:** Documents are updated but QA pairs remain old. Users get outdated guidance.

**Why it happens:**
- No update detection system
- Regeneration expensive
- No deployment pipeline for QA updates

**Warning signs:**
- Source documents have newer dates than QA generation
- User reports contradict QA pairs
- No process to refresh QA pairs

**Prevention strategy:**
- Track source document hashes
- Detect changes on scraper re-runs
- Implement selective regeneration (only changed docs)
- Include last_updated in QA metadata for cache invalidation

**Phase to address:** Maintenance phase (design for v5.0)

---

### E4: Context Window Overflow at Retrieval Time

**What goes wrong:** QA pairs work in isolation but retrieved context exceeds model limits. Production system truncates or fails.

**Why it happens:**
- QA generation uses full document context
- Retrieval returns multiple QA pairs + documents
- No length budgeting

**Warning signs:**
- Answers depend on context not included in QA pair
- Long answers fill context budget
- Multi-document queries fail

**Prevention strategy:**
- Generate self-contained answers (include necessary context)
- Track token counts per QA pair
- Set maximum answer length in generation prompt
- Test retrieval with realistic query patterns

**Phase to address:** QA Generation phase (design) + Integration testing

---

## Summary: Top 5 Critical Pitfalls

| Priority | Pitfall | Impact | Prevention Cost |
|----------|---------|--------|-----------------|
| 1 | P1: Hallucinated Procedure Steps | User follows wrong procedure | Medium (prompt engineering) |
| 2 | L2: Second-Language Accessibility | Target users cannot understand | Low (style guidelines) |
| 3 | D2: Role/Responsibility Confusion | Wrong person does task | Medium (role-specific QA) |
| 4 | V2: Ground Truth Absence | Cannot measure quality | High (human annotation) |
| 5 | E3: Stale QA Pairs | Outdated guidance in production | Medium (update detection) |

---

## Phase Mapping

| Phase | Pitfalls to Address |
|-------|---------------------|
| Planning | S1 (cost budget) |
| Document Analysis | D1 (dates), D3 (cross-refs), L3 (terminology) |
| Pipeline Design | P2 (attribution), S2 (rate limits), S3 (parallelization), E2 (traceability) |
| QA Generation | P1, P3, P4, L1, L2, D2, D4, E4 |
| Validation | V1, V2, V3, V4 |
| Export | E1 (format) |
| Maintenance | E3 (staleness) |

---

## Sources

**Quality and Hallucination:**
- [Learn Prompting: LLM Limitations](https://learnprompting.org/docs/basics/pitfalls)
- [HoneyHive: Avoiding Common Pitfalls in LLM Evaluation](https://www.honeyhive.ai/post/avoiding-common-pitfalls-in-llm-evaluation)
- [MDPI: Hallucination Mitigation for RAG](https://www.mdpi.com/2227-7390/13/5/856)
- [Ragas: Synthetic Data Generation](https://blog.ragas.io/all-about-synthetic-data-generation)

**Swedish NLP:**
- [Swedish Medical LLM Benchmark (SMLB)](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full)
- [AI Sweden: Swedish Language Data Lab](https://www.ai.se/en/project/swedish-language-data-lab)
- [Plain Swedish Language (Klarsprak)](https://www.isof.se/other-languages/english/plain-swedish-language)
- [KBLab: Evaluating Swedish Language Models](https://kb-labb.github.io/posts/2022-03-16-evaluating-swedish-language-models/)

**Scale and Cost:**
- [Anthropic API Pricing Guide](https://www.finout.io/blog/anthropic-api-pricing)
- [AI Batch Processing: OpenAI, Claude, Gemini](https://adhavpavan.medium.com/ai-batch-processing-openai-claude-and-gemini-2025-94107c024a10)
- [Anthropic Rate Limits](https://docs.anthropic.com/en/api/rate-limits)

**Evaluation:**
- [AIMultiple: LLM Evaluation Metrics](https://research.aimultiple.com/large-language-model-evaluation/)
- [Confident AI: LLM Evaluation Guide](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [Maxim: RAG Evaluation Guide 2025](https://www.getmaxim.ai/articles/rag-evaluation-a-complete-guide-for-2025)

**Healthcare/Domain:**
- [Nature: Framework for Clinical Safety and Hallucination Rates](https://www.nature.com/articles/s41746-025-01670-7)
- [Care Certificate Standards 2025 Updates](https://www.learningconnect.co.uk/Blog/blog_detail/faqs-for-update-care-certificate-standards-2025)

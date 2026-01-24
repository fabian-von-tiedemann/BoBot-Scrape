# Features Research: QA Generation Pipeline

**Domain:** Synthetic QA generation for Swedish municipal care procedures
**Researched:** 2026-01-24
**Overall Confidence:** MEDIUM-HIGH

---

## Table Stakes

Features users expect from any QA generation system. Missing = the pipeline is incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Document grounding** | Answers must trace to source documents | Medium | Every answer needs explicit source_url reference |
| **Groundedness verification** | Generated answers must be faithful to source | Medium | LLM-as-judge or RAGAS-style scoring |
| **Question diversity** | Cover factual, procedural, clarification types | Medium | Prevent repetitive "what is X?" patterns |
| **Batch processing** | Generate 1000s of QA pairs efficiently | Low | Reuse existing parallel Gemini pattern from convert.py |
| **Output format flexibility** | JSONL/CSV for different consumers | Low | Prompt context vs evaluation dataset have different needs |
| **Quality filtering** | Remove low-quality or unanswerable pairs | Medium | Two-stage: automated filters + optional manual review |
| **Source attribution** | Link each QA to originating document(s) | Low | Use existing frontmatter metadata |
| **Deduplication** | Avoid semantically redundant questions | Medium | Embedding similarity or hashing |

### Rationale

Research from [NVIDIA](https://developer.nvidia.com/blog/evaluating-and-enhancing-rag-pipeline-performance-using-synthetic-data/) and [AWS](https://aws.amazon.com/blogs/machine-learning/generate-synthetic-data-for-evaluating-rag-systems-using-amazon-bedrock/) confirms these are baseline requirements for any production synthetic QA system. The key quality dimensions are:

1. **Faithfulness/Groundedness** - Does the answer accurately reflect source content?
2. **Relevancy** - Is the question realistic and the answer responsive?
3. **Diversity** - Does the dataset cover the full range of document content?

---

## Differentiators

Features specific to Swedish municipal care worker context. These set BoBot apart.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Persona-driven questions** | Realistic queries from care worker perspectives | Medium | Role + situation + urgency modeling |
| **Swedish language optimization** | Natural phrasing for Swedish speakers | Low | Prompt engineering, not model fine-tuning |
| **Plain language answers** | Accessible to second-language speakers | Medium | CDC guidelines: short sentences, common words |
| **Mobile-first answer length** | Scannable on phone screens | Low | 2-3 sentences for facts, numbered steps for procedures |
| **Verksamhet-aware context** | Answers scoped to organizational unit | Low | Leverage existing category/subcategory metadata |
| **Stress-appropriate formatting** | Quick-reference for urgent situations | Medium | "Do X immediately, then Y, then Z" structure |
| **Cross-document synthesis** | Combine related procedures into single answer | High | For questions spanning multiple rutiner |

### Persona Model

Based on [Persona Hub research](https://arxiv.org/abs/2406.20094) and [Persona-SQ framework](https://arxiv.org/abs/2412.12445v1), model personas along these dimensions:

**Core Persona Attributes:**

| Attribute | Values | Impact on Questions |
|-----------|--------|---------------------|
| **Roll** | Underskoterska, Hemtjänstpersonal, Nattjour, Timanstallda, Enhetschef | Determines scope and detail level |
| **Erfarenhet** | Ny (< 6 man), Erfaren (1-3 ar), Senior (3+ ar) | New staff ask "what/how", seniors ask "when/why" |
| **Situation** | Rutinarbete, Akut, Osaker, Behover bekraftelse | Urgent = short answers, uncertain = more context |
| **Sprakbakgrund** | Svenska som forstassprak, Andrassprak | Second-language = simpler vocabulary |
| **Enhet** | Specific verksamhet from metadata | Scopes relevant procedures |

**Example Persona Instantiations:**

```yaml
persona_1:
  roll: underskoterska
  erfarenhet: ny
  situation: akut
  sprakbakgrund: andrassprak
  question_style: "Kort, konkret. Vad gor jag NU?"

persona_2:
  roll: enhetschef
  erfarenhet: senior
  situation: planering
  sprakbakgrund: svenska
  question_style: "Oversiktlig, vill ha bakgrund och regelreferens"

persona_3:
  roll: hemtjanstpersonal
  erfarenhet: erfaren
  situation: osaker
  sprakbakgrund: andrassprak
  question_style: "Behover bekraftelse pa att de gor ratt"
```

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in QA generation systems.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Fine-tuning data format** | Project scope is prompt context + eval, not model training | Generate for RAG retrieval and response evaluation |
| **Abstractive answers** | Risk hallucination, violates groundedness | Extractive/semi-extractive with explicit source quotes |
| **Self-enhancement evaluation** | Same LLM generating and judging = biased | Use different models or explicit verification against source text |
| **Unlimited answer length** | Care workers on mobile, under stress | Cap at 150 words for factual, 10 steps for procedural |
| **Complex multi-hop reasoning** | Source documents are self-contained procedures | Single-document grounding unless explicitly cross-doc |
| **Metadata-only questions** | "When was this document updated?" lacks utility | Focus on actionable procedure questions |
| **Exact text repetition** | Questions asking to recite document verbatim | Paraphrase understanding, not memorization |
| **Overly academic language** | Target users are field workers, not administrators | Plain Swedish, avoid formal "myndighetssprak" |

### Research-Backed Warnings

From [Prompt Engineering Guide](https://www.promptingguide.ai/applications/synthetic_rag):
> "Choose different LLMs for dataset creation than used for RAG generation in order to avoid self-enhancement bias."

From [Confident AI](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more):
> "Hallucination in RAG systems defeats the entire purpose of retrieval augmentation."

From [CDC Plain Language Guidelines](https://www.cdc.gov/health-literacy/php/develop-materials/plain-language.html):
> "Put the most important message first... strive for an average of 20 words per sentence."

---

## Question Types

Categories of questions to generate, mapped to care worker needs.

### Taxonomy (Adapted from Bloom + Domain-Specific)

| Type | Description | Example | Expected Volume |
|------|-------------|---------|-----------------|
| **Faktafragor** | "What is X?" basic recall | "Vad ar en delegering?" | 25% |
| **Procedurfragor** | "How do I do X?" step-by-step | "Hur gor jag vid fallolycka?" | 40% |
| **Situationsfragor** | "What if X happens?" conditional | "Vad gor jag om brukaren vagrar medicin?" | 20% |
| **Gransningsfragor** | "Am I doing X correctly?" validation | "Ska jag dokumentera detta i journalen?" | 10% |
| **Undantagsfragor** | "When does X NOT apply?" edge cases | "Nar far jag INTE ge medicin sjalv?" | 5% |

### Question Patterns by Document Type

Based on existing `document_type` metadata from frontmatter:

| Document Type | Likely Question Patterns |
|---------------|-------------------------|
| **Rutin** | How-to, step-by-step, sequence |
| **Policy** | What is allowed, what is required, exceptions |
| **Instruktion** | Specific procedure, equipment use |
| **Information** | What is X, who is responsible, contact info |
| **Checklista** | What to verify, in what order |
| **Blankett** | How to fill in, when to use |

---

## Answer Characteristics

What makes a good answer for this context.

### Quality Dimensions

| Dimension | Definition | Measurement |
|-----------|------------|-------------|
| **Groundedness** | Answer supported by source document | RAGAS faithfulness score > 0.8 |
| **Completeness** | All relevant info included | Manual review sampling |
| **Actionability** | User can act on the answer | Verb presence, concrete steps |
| **Brevity** | Appropriate length for mobile/stress | Word count < 150 for facts |
| **Clarity** | Understandable at first read | Sentence length < 20 words average |

### Adaptive Format Rules

```yaml
factual_question:
  format: "1-3 sentences stating the fact"
  max_words: 50
  example: "Delegering ar nar en sjukskoterska overlater en uppgift till dig. Det kravs skriftlig delegering och du maste ha fatt utbildning."

procedural_question:
  format: "Numbered steps, one action per step"
  max_steps: 10
  example: |
    1. Ring 112 omedelbart
    2. Stanna hos brukaren
    3. Folj instruktioner fran larmcentralen
    4. Dokumentera i journalen efterat

conditional_question:
  format: "If-then structure with clear trigger"
  max_words: 100
  example: "Om brukaren vagrar medicin: Dokumentera vagran. Informera sjukskoterska. Forsok inte tvinga. Notera tidpunkt och anledning om brukaren anger nagon."

validation_question:
  format: "Yes/No followed by brief rationale"
  max_words: 75
  example: "Ja, du ska dokumentera detta. Alla handelser som paverkar brukarens halsa ska journalforas samma dag enligt rutin."
```

### Source Citation Format

Every answer must include source attribution:

```yaml
answer_with_citation:
  text: "Vid fallolycka ska du forst sakerstalla att brukaren inte har skadat sig..."
  source:
    document: "Fallprevention - akuta atgarder"
    source_url: "https://botwebb.botkyrka.se/rutiner/vard/fallprevention.pdf"
    category: "Vard och omsorg"
    subcategory: "Sakerhet"
```

---

## Pipeline Architecture Recommendations

Based on research synthesis.

### Multi-Stage Generation

Following [NVIDIA SDG pipeline](https://developer.nvidia.com/blog/evaluating-and-enhancing-rag-pipeline-performance-using-synthetic-data/) and [multi-stage generation research](https://arxiv.org/abs/2509.25736):

```
Stage 1: Document Selection
  - Select document from KB
  - Extract key content chunks

Stage 2: Question Generation
  - Select persona from pool
  - Generate question matching persona style
  - Tag with question type

Stage 3: Answer Generation
  - Generate answer grounded in source
  - Apply adaptive formatting
  - Add source citation

Stage 4: Quality Filtering
  - Groundedness check (source verification)
  - Answerability check (is question clear?)
  - Deduplication (semantic similarity)
  - Diversity check (question type balance)
```

### Quality Thresholds

Based on [RAGAS framework](https://gist.github.com/donbr/1a1281f647419aaacb8673223b69569c):

| Metric | Threshold | Action if Below |
|--------|-----------|-----------------|
| Faithfulness | > 0.8 | Regenerate answer |
| Answer Relevancy | > 0.7 | Regenerate question |
| Context Relevancy | > 0.6 | Select different chunk |
| Overall Quality | > 0.7 | Reject pair |

### Cost Estimation

From [AWS research](https://aws.amazon.com/blogs/machine-learning/generate-synthetic-data-for-evaluating-rag-systems-using-amazon-bedrock/):
> "The generation of 1,000 sets of questions and answers costs approximately $2.80 USD using Anthropic Claude 3 Haiku."

For BoBot target of ~5,000 QA pairs with Gemini:
- Estimated cost: $15-30 (depends on model choice)
- Estimated time: 2-4 hours with parallel processing

---

## Feature Dependencies

```
Document grounding ─────┬──> Groundedness verification
                        │
Persona model ──────────┼──> Question generation ──> Quality filtering
                        │
Verksamhet metadata ────┘

Quality filtering ──────┬──> Deduplication
                        │
Adaptive formatting ────┴──> Output export
```

### Implementation Order Recommendation

1. **Phase 1: Core Generation**
   - Document selection from KB
   - Basic question generation (no personas yet)
   - Answer generation with source citation
   - Simple groundedness check

2. **Phase 2: Quality Layer**
   - Full groundedness verification
   - Deduplication
   - Quality filtering
   - JSONL export

3. **Phase 3: Persona Enhancement**
   - Persona model implementation
   - Persona-driven question variety
   - Adaptive answer formatting

4. **Phase 4: Scale & Polish**
   - Batch processing optimization
   - Statistics and coverage reports
   - Manual review workflow

---

## MVP Recommendation

For v5.0 MVP, prioritize:

1. **Table stakes:**
   - Document grounding (mandatory)
   - Groundedness verification (mandatory)
   - Question diversity via type tags (mandatory)
   - Batch processing (reuse existing patterns)
   - JSONL output format

2. **One differentiator:**
   - Simple persona model (roll + situation)

**Defer to post-MVP:**
- Cross-document synthesis (High complexity, rarely needed)
- Full RAGAS evaluation suite (can use simpler checks initially)
- Manual review workflow (start with automated filters)

---

## Sources

### High Confidence (Official/Research)
- [NVIDIA: Evaluating and Enhancing RAG Pipeline Performance Using Synthetic Data](https://developer.nvidia.com/blog/evaluating-and-enhancing-rag-pipeline-performance-using-synthetic-data/)
- [AWS: Generate synthetic data for evaluating RAG systems](https://aws.amazon.com/blogs/machine-learning/generate-synthetic-data-for-evaluating-rag-systems-using-amazon-bedrock/)
- [Persona Hub: Scaling Synthetic Data Creation](https://arxiv.org/abs/2406.20094)
- [Persona-SQ: Personalized Suggested Question Generation](https://arxiv.org/abs/2412.12445v1)
- [RAGAS Framework Documentation](https://gist.github.com/donbr/1a1281f647419aaacb8673223b69569c)

### Medium Confidence (WebSearch Verified)
- [Confident AI: RAG Evaluation Metrics](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)
- [Prompt Engineering Guide: Synthetic RAG Data](https://www.promptingguide.ai/applications/synthetic_rag)
- [CDC: Plain Language Materials & Resources](https://www.cdc.gov/health-literacy/php/develop-materials/plain-language.html)
- [Multi-Stage Domain-Grounded Synthetic Data Generation](https://arxiv.org/abs/2509.25736)

### Domain-Specific Context
- [Swedish Medical LLM Benchmark](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1557920/full) - Swedish language LLM evaluation challenges
- [GPT-SW3: Autoregressive Language Model for Scandinavian Languages](https://arxiv.org/abs/2305.12987) - Swedish-specific NLP considerations

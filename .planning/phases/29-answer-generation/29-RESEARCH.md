# Phase 29: Answer Generation - Research

**Researched:** 2026-01-29
**Domain:** Semantic retrieval, LLM answer generation with citations, klarsprak Swedish
**Confidence:** HIGH

## Summary

Phase 29 generates grounded answers with explicit source citations for questions created in Phase 28. The core workflow is: (1) embed questions for semantic search, (2) retrieve top-5 relevant document chunks, (3) generate answers grounded in retrieved content using Gemini 2.0 Flash, (4) format with inline citations and klarsprak Swedish.

The standard approach uses KBLab's Swedish sentence-BERT (`KBLab/sentence-bert-swedish-cased`) for embeddings since it's trained specifically for Swedish text. For vector search, FAISS (`faiss-cpu`) provides efficient similarity search without heavy infrastructure. Document chunking uses 512 tokens with 25% overlap (128 tokens) for optimal retrieval precision. Answer generation uses the existing Gemini integration pattern with a new Pydantic model for structured answer output including citations.

**Primary recommendation:** Use KBLab Swedish SBERT for embeddings, FAISS for vector search, 512-token chunks with overlap, and Gemini 2.0 Flash with structured output for citation-grounded answers in klarsprak Swedish.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sentence-transformers | >=2.2.0 | Embedding generation | Industry standard for sentence embeddings |
| KBLab/sentence-bert-swedish-cased | - | Swedish embeddings | Native Swedish model, 0.918 Pearson on SweParaphrase |
| faiss-cpu | >=1.7.0 | Vector similarity search | Fast, efficient, no external service needed |
| google-genai | >=1.0.0 | Gemini API for answer generation | Already installed, proven in codebase |
| pydantic | >=2.0.0 | Structured output schemas | Already installed, used for response_schema |
| tiktoken | >=0.5.0 | Token counting for chunking | OpenAI-compatible tokenizer, accurate counts |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| numpy | >=1.24.0 | Array operations for embeddings | Required by sentence-transformers and FAISS |
| pyyaml | 6.0.x | Read questions, write QA output | Already installed |
| rich | 14.x | Progress bars for batch processing | Already installed from Phase 28 |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| KBLab Swedish SBERT | paraphrase-multilingual-MiniLM-L12-v2 | Multilingual but less optimized for Swedish |
| FAISS | chromadb, pinecone | External service/heavier dependency, FAISS simpler for local use |
| tiktoken | transformers tokenizer | Simpler API, sufficient for chunking |
| Gemini 2.0 Flash | GPT-4 | Gemini already in stack, good Swedish support |

**Installation:**
```bash
pip install sentence-transformers faiss-cpu tiktoken
# sentence-transformers will install torch automatically
```

## Architecture Patterns

### Recommended Project Structure
```
src/
└── qa/
    ├── __init__.py          # Export answer generation functions
    ├── persona.py           # Existing from Phase 27
    ├── question.py          # Existing from Phase 28
    ├── answer.py            # NEW: Answer generation logic
    ├── retriever.py         # NEW: Semantic retrieval with FAISS
    └── chunker.py           # NEW: Document chunking utilities
qa/
├── questions.yaml           # Input from Phase 28
├── answers.yaml             # NEW: Output QA pairs
└── embeddings/              # NEW: Cached FAISS index
    ├── chunks.index         # FAISS index file
    └── chunks_meta.json     # Chunk metadata (document, section)
generate_qa.py               # Extend CLI with answer generation
```

### Pattern 1: Document Chunking with Overlap
**What:** Split documents into 512-token chunks with 128-token overlap
**When to use:** Before embedding, once per document corpus
**Example:**
```python
# Source: Microsoft RAG chunking guidelines, tiktoken docs
import tiktoken
from pathlib import Path
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """A chunk of a document with metadata."""
    content: str
    document_path: str  # Relative path: category/filename.md
    section: str  # Nearest heading or empty
    chunk_index: int
    token_count: int

def chunk_document(
    document_path: Path,
    chunk_size: int = 512,
    overlap: int = 128,
    encoding_name: str = "cl100k_base"
) -> list[DocumentChunk]:
    """Split document into overlapping token chunks."""
    enc = tiktoken.get_encoding(encoding_name)

    with open(document_path, encoding='utf-8') as f:
        content = f.read()

    # Skip frontmatter
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            content = content[end+3:].strip()

    # Tokenize
    tokens = enc.encode(content)

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)

        # Extract nearest section heading
        section = extract_section_heading(chunk_text)

        chunks.append(DocumentChunk(
            content=chunk_text,
            document_path=str(document_path.relative_to(document_path.parent.parent)),
            section=section,
            chunk_index=chunk_index,
            token_count=len(chunk_tokens)
        ))

        start += chunk_size - overlap
        chunk_index += 1

    return chunks

def extract_section_heading(text: str) -> str:
    """Extract the last markdown heading from text."""
    import re
    headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
    return headings[-1] if headings else ""
```

### Pattern 2: Swedish Sentence Embeddings with FAISS Index
**What:** Create and query FAISS index using Swedish SBERT embeddings
**When to use:** Retrieval step for each question
**Example:**
```python
# Source: sentence-transformers docs, FAISS documentation
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from pathlib import Path

class SwedishRetriever:
    """Semantic retriever using Swedish SBERT and FAISS."""

    def __init__(self, index_dir: Path):
        self.model = SentenceTransformer('KBLab/sentence-bert-swedish-cased')
        self.index_dir = index_dir
        self.index = None
        self.chunks_meta = []

    def build_index(self, chunks: list[DocumentChunk]) -> None:
        """Build FAISS index from document chunks."""
        # Generate embeddings
        texts = [c.content for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Create index (IndexFlatIP for inner product = cosine after normalization)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        # Store metadata
        self.chunks_meta = [
            {
                "content": c.content,
                "document_path": c.document_path,
                "section": c.section,
                "chunk_index": c.chunk_index
            }
            for c in chunks
        ]

        # Save to disk
        self.index_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_dir / "chunks.index"))
        with open(self.index_dir / "chunks_meta.json", 'w', encoding='utf-8') as f:
            json.dump(self.chunks_meta, f, ensure_ascii=False, indent=2)

    def load_index(self) -> None:
        """Load existing FAISS index from disk."""
        self.index = faiss.read_index(str(self.index_dir / "chunks.index"))
        with open(self.index_dir / "chunks_meta.json", encoding='utf-8') as f:
            self.chunks_meta = json.load(f)

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """Retrieve top-k chunks for a query."""
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)

        scores, indices = self.index.search(query_embedding, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks_meta):
                result = self.chunks_meta[idx].copy()
                result["score"] = float(score)
                results.append(result)

        return results
```

### Pattern 3: Answer Generation with Citations (Klarsprak)
**What:** Generate grounded answers with inline citations using Gemini
**When to use:** For each question after retrieval
**Example:**
```python
# Source: Gemini structured output docs, CONTEXT.md klarsprak requirements
from pydantic import BaseModel, Field
from typing import Literal
import os
from google import genai
from google.genai import types

class Citation(BaseModel):
    """A citation to a source document."""
    document: str = Field(description="Full document path, e.g., rutiner/handtvatt.md")
    section: str = Field(description="Section heading if available, empty otherwise")

class GeneratedAnswer(BaseModel):
    """A grounded answer with citations."""
    answer: str = Field(
        description="Svar pa klarsprak svenska (B1-niva, max 15 ord per mening, aktiv form)"
    )
    citations: list[Citation] = Field(
        min_length=1,
        description="Kallor som stodjer svaret"
    )
    coverage: Literal["full", "partial", "none"] = Field(
        description="Hur val kallorna tackte fragan"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Konfidensgrad for svaret"
    )

ANSWER_GENERATION_PROMPT = '''Du ar en erfaren kollega som ger korta, tydliga svar pa svenska.

## Klarsprakskrav (VIKTIGT)
- Max 15 ord per mening
- Anvand aktiv form: "Du tvattar handerna" INTE "Handerna ska tvattas"
- Tilltala med "du" konsekvent
- Vanligt ordforrad, undvik facktermer om mojligt
- Om fackterm anvands, forklara kort: "Dekubitus (tryckskada) kraver..."

## Citering
- Varje pastende maste ha en kallhanvisning: [source:dokument.md#sektion]
- Om sektionen saknas, ange bara dokumentet: [source:dokument.md]
- Flera kallor: "X [source:doc1.md]. Y [source:doc2.md]."

## Svarsformat
- Kort svar: 1-3 meningar
- Citera endast vid exakta formuleringar (doser, regler, procedurer)
- Om kallorna inte besvarar fragan helt: "Svaret ar ofullstandigt. Kallorna beskriver X men inte Y."

## Fraga
{question}

## Kallor
{sources}

Ge ett grundat svar:
'''

def generate_answer(
    question: str,
    retrieved_chunks: list[dict],
    delay: float = 0.2
) -> GeneratedAnswer | None:
    """Generate grounded answer using Gemini."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return None

    # Format sources for prompt
    sources_text = ""
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_ref = chunk["document_path"]
        if chunk.get("section"):
            source_ref += f"#{chunk['section'].lower().replace(' ', '-')}"
        sources_text += f"\n### Kalla {i}: {source_ref}\n{chunk['content']}\n"

    prompt = ANSWER_GENERATION_PROMPT.format(
        question=question,
        sources=sources_text
    )

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedAnswer,
            )
        )

        import time
        if delay > 0:
            time.sleep(delay)

        return response.parsed

    except Exception as e:
        import logging
        logging.warning(f"Answer generation failed: {e}")
        return None
```

### Pattern 4: Complete QA Entry for Output
**What:** Full QA pair with all metadata for YAML output
**When to use:** Final output structure
**Example:**
```python
# Source: CONTEXT.md requirements, Phase 28 output format
from pydantic import BaseModel
from datetime import datetime

class QAEntry(BaseModel):
    """Complete question-answer pair for output."""
    question: str
    answer: str
    citations: list[dict]  # [{document: str, section: str}]
    coverage: str  # full, partial, none
    confidence: float
    source_document: str  # Original question source
    section: str  # Original question section
    question_type: str
    persona: dict
    category: str
    generated_at: str

def create_qa_entry(
    question_entry: dict,  # From questions.yaml
    answer: GeneratedAnswer
) -> QAEntry:
    """Combine question and answer into full QA entry."""
    return QAEntry(
        question=question_entry["question"],
        answer=answer.answer,
        citations=[c.model_dump() for c in answer.citations],
        coverage=answer.coverage,
        confidence=answer.confidence,
        source_document=question_entry["source_document"],
        section=question_entry["section"],
        question_type=question_entry["question_type"],
        persona=question_entry["persona"],
        category=question_entry["category"],
        generated_at=datetime.now().isoformat()
    )
```

### Anti-Patterns to Avoid
- **Embedding entire documents:** Don't embed whole documents; use 512-token chunks for precision
- **Using English embedding models for Swedish:** Don't use all-MiniLM-L6-v2; use KBLab Swedish SBERT
- **Hand-rolling vector search:** Don't implement cosine similarity manually; use FAISS
- **Generating answers without grounding prompt:** Don't let model make up facts; require citations
- **Passive voice in klarsprak:** Don't accept "Handerna ska tvattas"; require "Du tvattar handerna"
- **Long sentences:** Don't generate >15 word sentences; verify in output

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Text embeddings | TF-IDF, word2vec | sentence-transformers | Captures semantic meaning |
| Swedish embeddings | Multilingual model | KBLab/sentence-bert-swedish-cased | Trained on Swedish, better accuracy |
| Vector similarity search | Numpy cosine | FAISS IndexFlatIP | Optimized, scales to millions |
| Token counting | len(text.split()) | tiktoken | Accurate token counts for LLM context |
| Citation formatting | String manipulation | Structured output schema | Model enforces format |
| Klarsprak enforcement | Post-processing | Prompt engineering | Model applies rules during generation |

**Key insight:** The retrieval step requires real semantic understanding of Swedish text. KBLab's Swedish SBERT was trained specifically for this, achieving 0.918 Pearson correlation on Swedish paraphrase benchmarks.

## Common Pitfalls

### Pitfall 1: Embedding Model Mismatch
**What goes wrong:** Questions don't retrieve relevant chunks
**Why it happens:** Using English embedding model for Swedish text
**How to avoid:** Use KBLab/sentence-bert-swedish-cased specifically
**Warning signs:** Low relevance scores (<0.5), irrelevant chunks retrieved

### Pitfall 2: Chunk Size Too Small/Large
**What goes wrong:** Retrieved content lacks context OR is too unfocused
**Why it happens:** 256 tokens too granular, 1024 tokens too broad
**How to avoid:** Start with 512 tokens + 128 overlap per Microsoft guidelines
**Warning signs:** Answers reference "partial" information, or answers are vague

### Pitfall 3: Citations Not Grounded
**What goes wrong:** Model generates citations that don't match retrieved chunks
**Why it happens:** Prompt doesn't enforce grounding strictly enough
**How to avoid:** Include exact source paths in prompt, validate citations exist
**Warning signs:** Citations reference non-existent documents or sections

### Pitfall 4: Passive Voice in Klarsprak
**What goes wrong:** Answers use formal Swedish instead of klarsprak
**Why it happens:** Model defaults to formal register
**How to avoid:** Explicit examples in prompt, post-validation for passive constructions
**Warning signs:** "ska + verb" constructions, long sentences, formal vocabulary

### Pitfall 5: FAISS Index Not Persisted
**What goes wrong:** Index rebuilt on every run, slow startup
**Why it happens:** Forgetting to save/load index
**How to avoid:** Use faiss.write_index/read_index, store metadata alongside
**Warning signs:** Long startup time, "building index" message every run

### Pitfall 6: Rate Limiting on Batch Processing
**What goes wrong:** 429 errors during answer generation
**Why it happens:** Too many parallel API calls
**How to avoid:** Same pattern as Phase 28: max_workers=5, delay=0.2s
**Warning signs:** API errors, incomplete processing

### Pitfall 7: Section References Lost in Chunks
**What goes wrong:** Citations can't include section because chunk metadata lacks it
**Why it happens:** Chunking doesn't preserve section context
**How to avoid:** Extract section heading from chunk text, store in metadata
**Warning signs:** All citations missing section, just document path

## Code Examples

Verified patterns from official sources:

### Complete Answer Generation Pipeline
```python
# Source: Patterns above combined
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress
import yaml

def generate_answers_batch(
    questions_file: Path,
    retriever: SwedishRetriever,
    output_file: Path,
    max_workers: int = 5,
    delay: float = 0.2
) -> None:
    """Generate answers for all questions with progress tracking."""
    # Load questions from Phase 28 output
    with open(questions_file, encoding='utf-8') as f:
        questions_data = yaml.safe_load(f)

    # Flatten questions from all categories
    all_questions = []
    for category, questions in questions_data["categories"].items():
        all_questions.extend(questions)

    all_qa_entries = []

    def process_single(q: dict) -> QAEntry | None:
        # Retrieve relevant chunks
        chunks = retriever.retrieve(q["question"], top_k=5)
        if not chunks:
            return None

        # Generate answer
        answer = generate_answer(q["question"], chunks, delay=delay)
        if not answer:
            return None

        return create_qa_entry(q, answer)

    with Progress() as progress:
        task = progress.add_task("Generating answers...", total=len(all_questions))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for result in executor.map(process_single, all_questions):
                if result:
                    all_qa_entries.append(result)
                progress.advance(task)

    # Write output
    output = {
        "generated_at": datetime.now().isoformat(),
        "total_qa_pairs": len(all_qa_entries),
        "questions_processed": len(all_questions),
        "categories": {}
    }

    # Group by category
    for entry in all_qa_entries:
        cat = entry.category
        if cat not in output["categories"]:
            output["categories"][cat] = []
        output["categories"][cat].append(entry.model_dump())

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
```

### Index Building Script
```python
# Source: Chunking and retrieval patterns above
def build_embeddings_index(
    documents_dir: Path,
    index_dir: Path,
    chunk_size: int = 512,
    overlap: int = 128
) -> None:
    """Build FAISS index from all documents."""
    # Collect all markdown files
    md_files = list(documents_dir.rglob("*.md"))
    print(f"Found {len(md_files)} documents")

    # Chunk all documents
    all_chunks = []
    for md_file in md_files:
        chunks = chunk_document(md_file, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)

    print(f"Created {len(all_chunks)} chunks")

    # Build index
    retriever = SwedishRetriever(index_dir)
    retriever.build_index(all_chunks)

    print(f"Index saved to {index_dir}")
```

### Klarsprak Validation Helper
```python
# Source: CONTEXT.md klarsprak requirements
import re

def validate_klarsprak(text: str) -> list[str]:
    """Check text against klarsprak guidelines, return warnings."""
    warnings = []

    sentences = re.split(r'[.!?]', text)
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 15:
            warnings.append(f"Long sentence ({len(words)} words): {sentence[:50]}...")

    # Check for passive voice indicators
    passive_patterns = [
        r'\b(ska|bor|maste)\s+\w+s\b',  # "ska tvattas"
        r'\b\w+as\s+av\b',  # "utfors av"
    ]
    for pattern in passive_patterns:
        if re.search(pattern, text.lower()):
            warnings.append(f"Possible passive voice: {pattern}")

    return warnings
```

### Expected Output Format
```yaml
# qa/answers.yaml
generated_at: "2026-01-29T14:30:00"
total_qa_pairs: 4587
questions_processed: 4600
categories:
  Hemtjanst:
    - question: "Jag ar ny i hemtjansten och undrar - hur ofta ska arbetskladerna bytas?"
      answer: "Du byter arbetsklader varje dag. Om de blir smutsiga byter du dem direkt [source:Hemtjanst/basal-hygien.md#arbetsklader]."
      citations:
        - document: "Hemtjanst/basal-hygien.md"
          section: "arbetsklader"
      coverage: "full"
      confidence: 0.95
      source_document: "Hemtjanst/Rutin basal hygien arbetsklader.md"
      section: "Hur gor du?"
      question_type: "procedural"
      persona:
        roll: "underskoterska"
        erfarenhet: "nyanstald"
        situation: "forsta manaden i hemtjansten"
        sprakbakgrund: "native"
      category: "Hemtjanst"
      generated_at: "2026-01-29T14:25:12"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| TF-IDF retrieval | Dense vector retrieval | 2020+ | Better semantic matching |
| English multilingual models | Language-specific models | 2023+ | Higher accuracy for Swedish |
| Post-hoc citation addition | Inline citation generation | 2024+ | More accurate grounding |
| Large chunks (1000+ tokens) | 512 tokens with overlap | 2025 | Better retrieval precision |

**Deprecated/outdated:**
- `google-generativeai` package - use `google-genai>=1.0.0`
- `gemini-3-flash-preview` - not available, use `gemini-2.0-flash`
- Naive BM25 retrieval - insufficient for semantic questions

**Note:** Gemini 2.0 Flash and Flash-Lite models will be retired on March 3, 2026. Plan migration to `gemini-2.5-flash-lite` for long-term stability.

## Open Questions

Things that couldn't be fully resolved:

1. **Optimal top-k for retrieval**
   - What we know: CONTEXT.md specifies 5 chunks
   - What's unclear: Whether 5 is optimal for all question types
   - Recommendation: Start with 5, track coverage scores, adjust if many "partial"

2. **Section heading extraction accuracy**
   - What we know: Regex-based extraction works for markdown headings
   - What's unclear: How well it handles documents without clear heading structure
   - Recommendation: Fall back to empty section if no heading found

3. **Klarsprak enforcement reliability**
   - What we know: Prompt instructs B1 Swedish, max 15 words
   - What's unclear: How consistently Gemini follows these constraints
   - Recommendation: Add post-validation, flag violations for review

4. **Index rebuild frequency**
   - What we know: Documents from Phase 28 are static
   - What's unclear: If new documents will be added later
   - Recommendation: Build once, add rebuild command for future updates

## Sources

### Primary (HIGH confidence)
- [KBLab Swedish Sentence-BERT](https://huggingface.co/KBLab/sentence-bert-swedish-cased) - Swedish embedding model
- [KBLab Blog: Swedish Sentence Transformer 2.0](https://kb-labb.github.io/posts/2023-01-16-sentence-transformer-20/) - Model capabilities
- [FAISS Documentation](https://faiss.ai/) - Vector search implementation
- [Sentence Transformers Documentation](https://www.sbert.net/) - Embedding library usage
- [Microsoft RAG Chunking Guide](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents) - 512 token recommendation
- [Google GenAI SDK](https://googleapis.github.io/python-genai/) - Structured output with Pydantic

### Secondary (MEDIUM confidence)
- [Weaviate Chunking Strategies](https://weaviate.io/blog/chunking-strategies-for-rag) - Overlap recommendations
- [Research: Effective LLM Adaptation for Grounding](https://arxiv.org/abs/2311.09533) - Citation generation patterns
- [Institutet for sprak och folkminnen - Klarsprak](https://www.isof.se/other-languages/english/plain-swedish-language) - Swedish plain language guidelines

### Tertiary (LOW confidence)
- WebSearch results on B1 Swedish level - general CEFR guidelines, not specific klarsprak implementation

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Established libraries, proven for Swedish text
- Architecture: HIGH - Clear patterns from existing codebase and research
- Retrieval: HIGH - FAISS well-documented, Swedish SBERT benchmarked
- Answer generation: MEDIUM - Prompt engineering for klarsprak needs validation
- Citation accuracy: MEDIUM - Depends on model following grounding instructions

**Research date:** 2026-01-29
**Valid until:** 2026-02-28 (Gemini API evolves quickly, embedding models stable)

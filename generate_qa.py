#!/usr/bin/env python3
"""
QA Generation Pipeline: Generate Q&A pairs from converted documents.

Generates persona-based question and answer pairs from markdown documents
for training AI assistants. Each persona represents a care worker with
different experience levels and Swedish proficiency.

Usage:
    python generate_qa.py --input converted/ --output qa/
    python generate_qa.py --personas config/custom.yaml
    python generate_qa.py --file converted/doc.md --verbose
    python generate_qa.py --limit 10
    python generate_qa.py --build-index
    python generate_qa.py --answers --limit 10
"""
import argparse
import logging
import random
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / '.env')

from src.qa import (
    Persona,
    load_personas,
    generate_questions_for_document,
    process_documents_batch,
    deduplicate_questions,
    write_questions_yaml,
    # Chunking and retrieval
    chunk_all_documents,
    SwedishRetriever,
    # Answer generation
    generate_answers_batch,
    # Checkpoint
    Checkpoint,
    compute_dir_hash,
    save_checkpoint,
    load_checkpoint,
    should_skip_stage,
    delete_checkpoint,
)
from src.qa.question import select_persona_for_document


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs from converted documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Use defaults (generate questions)
  %(prog)s --input converted/           Custom input directory
  %(prog)s --personas config/p.yaml     Custom persona config
  %(prog)s --file converted/doc.md      Single file mode (for testing)
  %(prog)s --limit 10                   Process only 10 documents
  %(prog)s --build-index                Build FAISS index from documents
  %(prog)s --answers                    Generate answers for questions.yaml
  %(prog)s --answers --limit 10         Generate answers for first 10 questions
  %(prog)s --validate                   Validate QA pairs from answers.yaml
  %(prog)s --export                     Export to HuggingFace JSONL format
        """
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path("converted/"),
        help="Input directory with markdown documents (default: converted/)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("qa/"),
        help="Output directory for Q&A files (default: qa/)"
    )
    parser.add_argument(
        "--personas",
        type=Path,
        default=Path("config/personas.yaml"),
        help="Persona configuration file (default: config/personas.yaml)"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Process single file (for testing)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of documents/questions to process"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    # Answer generation arguments
    parser.add_argument(
        "--build-index",
        action="store_true",
        help="Build/rebuild FAISS index from converted/ documents"
    )
    parser.add_argument(
        "--answers",
        action="store_true",
        help="Generate answers for questions.yaml (requires index)"
    )
    parser.add_argument(
        "--questions-file",
        type=Path,
        default=Path("qa/questions.yaml"),
        help="Path to questions YAML (default: qa/questions.yaml)"
    )
    parser.add_argument(
        "--index-dir",
        type=Path,
        default=Path("qa/embeddings"),
        help="Path to embeddings index directory (default: qa/embeddings)"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate QA pairs from answers.yaml, output to qa_passed.jsonl and qa_rejected.jsonl"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export validated QA pairs to HuggingFace-compatible JSONL format"
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore checkpoint and run fresh (don't resume)"
    )
    return parser.parse_args()


def build_index_command(args) -> int:
    """Build FAISS index from converted documents."""
    print(f"Building FAISS index from {args.input}...")

    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        return 1

    # Chunk all documents
    print()
    chunks = chunk_all_documents(args.input)

    if not chunks:
        print("No chunks created (no markdown documents found)")
        return 1

    print(f"\nCreated {len(chunks)} chunks from documents")

    # Build index
    print(f"\nBuilding index in {args.index_dir}...")
    retriever = SwedishRetriever(args.index_dir)
    retriever.build_index(chunks)

    print(f"\nIndex saved to {args.index_dir}")
    print(f"  - chunks.index: FAISS index file")
    print(f"  - chunks_meta.json: Chunk metadata")

    return 0


def export_command(args) -> int:
    """Export validated QA pairs to HuggingFace-compatible JSONL format."""
    print("Export mode")

    # Check qa_passed.jsonl exists
    passed_path = args.output / "qa_passed.jsonl"
    if not passed_path.exists():
        print(f"Error: qa_passed.jsonl not found at {passed_path}")
        print("Run with --validate first to generate validated QA pairs")
        return 1

    from src.qa import export_hf_jsonl

    # Export passed pairs
    print(f"\nExporting passed pairs from {passed_path}...")
    output_passed = args.output / "qa_pairs.jsonl"
    passed_stats = export_hf_jsonl(
        input_path=passed_path,
        output_path=output_passed,
        include_rejected=False
    )

    # Export rejected pairs if they exist
    rejected_path = args.output / "qa_rejected.jsonl"
    rejected_stats = {"total": 0, "exported": 0}
    if rejected_path.exists():
        print(f"Exporting rejected pairs from {rejected_path}...")
        output_rejected = args.output / "qa_rejected_hf.jsonl"
        rejected_stats = export_hf_jsonl(
            input_path=rejected_path,
            output_path=output_rejected,
            include_rejected=True
        )

    # Print summary
    print(f"\n=== Export Summary ===")
    print(f"Passed pairs: {passed_stats['exported']} -> {output_passed}")
    if rejected_stats['exported'] > 0:
        print(f"Rejected pairs: {rejected_stats['exported']} -> {args.output / 'qa_rejected_hf.jsonl'}")

    print(f"\nHuggingFace usage:")
    print(f"  from datasets import load_dataset")
    print(f"  dataset = load_dataset('json', data_files='{output_passed}')")

    return 0


def validate_command(args) -> int:
    """Validate QA pairs from answers.yaml."""
    print("Validation mode")

    # Check answers file exists
    answers_path = args.output / "answers.yaml"
    if not answers_path.exists():
        print(f"Error: answers.yaml not found at {answers_path}")
        print("Run with --answers first to generate QA pairs")
        return 1

    # Check index exists
    index_file = args.index_dir / "chunks.index"
    if not index_file.exists():
        print(f"Error: Index not found at {args.index_dir}")
        print("Run --build-index first to create the FAISS index")
        return 1

    # Load answers
    print(f"\nLoading answers from {answers_path}...")
    with open(answers_path, encoding='utf-8') as f:
        answers_data = yaml.safe_load(f)

    # Flatten categories to list
    qa_pairs = []
    for category, entries in answers_data.get('categories', {}).items():
        qa_pairs.extend(entries)

    print(f"Found {len(qa_pairs)} QA pairs in {len(answers_data.get('categories', {}))} categories")

    # Load retriever and documents
    from src.qa import SwedishRetriever, validate_batch, load_document_contents

    print(f"\nLoading index from {args.index_dir}...")
    retriever = SwedishRetriever(args.index_dir)
    retriever.load_index()

    print(f"Loading documents from {args.input}...")
    doc_contents = load_document_contents(Path(args.input))
    print(f"Loaded {len(doc_contents)} documents")

    # Run validation
    print("\nRunning validation...")
    print()
    stats = validate_batch(
        qa_pairs=qa_pairs,
        retriever=retriever,
        doc_contents=doc_contents,
        output_passed=args.output / "qa_passed.jsonl",
        output_rejected=args.output / "qa_rejected.jsonl",
        threshold=0.7
    )

    # Print summary
    print(f"\n=== Validation Summary ===")
    print(f"Total pairs: {stats['total']}")
    print(f"Passed: {stats['passed']} ({stats['pass_rate']:.1%})")
    print(f"Rejected: {stats['rejected']}")
    print(f"Average score (passed): {stats['avg_score']:.2f}")
    print(f"\nOutput files:")
    print(f"  Passed: {args.output / 'qa_passed.jsonl'}")
    print(f"  Rejected: {args.output / 'qa_rejected.jsonl'}")

    return 0


def generate_answers_command(args) -> int:
    """Generate answers for questions using retrieval and Gemini."""
    print("Generate answers mode")

    # Check questions file exists
    if not args.questions_file.exists():
        print(f"Error: Questions file {args.questions_file} does not exist")
        print("Run without --answers first to generate questions")
        return 1

    # Check index exists
    index_file = args.index_dir / "chunks.index"
    if not index_file.exists():
        print(f"Error: Index not found at {args.index_dir}")
        print("Run --build-index first to create the FAISS index")
        return 1

    # Load questions
    print(f"\nLoading questions from {args.questions_file}...")
    with open(args.questions_file, encoding='utf-8') as f:
        questions_data = yaml.safe_load(f)

    # Flatten questions from all categories
    all_questions = []
    for category, questions in questions_data.get("categories", {}).items():
        all_questions.extend(questions)

    print(f"Found {len(all_questions)} questions in {len(questions_data.get('categories', {}))} categories")

    # Load retriever
    print(f"\nLoading index from {args.index_dir}...")
    retriever = SwedishRetriever(args.index_dir)
    retriever.load_index()

    # Generate answers
    output_file = args.output / "answers.yaml"
    print(f"\nGenerating answers...")
    if args.limit:
        print(f"(limited to {args.limit} questions)")
    print()

    count = generate_answers_batch(
        questions=all_questions,
        retriever=retriever,
        output_path=output_file,
        max_workers=5,
        delay=0.2,
        limit=args.limit
    )

    print(f"\nGenerated {count} QA pairs")
    print(f"Saved to {output_file}")

    # Show summary
    if args.verbose and output_file.exists():
        with open(output_file, encoding='utf-8') as f:
            answers_data = yaml.safe_load(f)
        print("\nQA pairs by category:")
        for cat, entries in answers_data.get("categories", {}).items():
            print(f"  {cat}: {len(entries)}")

    return 0


def get_checkpoint_path(output_dir: Path) -> Path:
    """Get checkpoint file path for output directory."""
    return output_dir / ".checkpoint.json"


def update_checkpoint(
    checkpoint_path: Path,
    stage: str,
    input_hash: str,
    completed_stages: list[str]
) -> None:
    """Update checkpoint after completing a stage."""
    from datetime import datetime, timezone
    checkpoint = Checkpoint(
        stage=stage,
        input_hash=input_hash,
        completed_stages=completed_stages,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
    save_checkpoint(checkpoint_path, checkpoint)


def main():
    """Run the QA generation pipeline."""
    args = parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Checkpoint setup
    checkpoint_path = get_checkpoint_path(args.output)
    checkpoint = None if args.no_resume else load_checkpoint(checkpoint_path)
    input_hash = compute_dir_hash(args.input) if args.input.exists() else ""

    if checkpoint and not args.no_resume:
        if checkpoint.input_hash == input_hash:
            print(f"Resuming from checkpoint (completed: {', '.join(checkpoint.completed_stages)})")
        else:
            print("Input changed since checkpoint - starting fresh")
            checkpoint = None

    completed_stages = list(checkpoint.completed_stages) if checkpoint else []

    # Handle --build-index mode
    if args.build_index:
        if should_skip_stage(checkpoint, "index", input_hash):
            print("Skipping index stage (already completed)")
            return 0
        result = build_index_command(args)
        if result == 0:
            completed_stages.append("index")
            update_checkpoint(checkpoint_path, "index", input_hash, completed_stages)
        return result

    # Handle --answers mode
    if args.answers:
        if should_skip_stage(checkpoint, "answers", input_hash):
            print("Skipping answers stage (already completed)")
            return 0
        result = generate_answers_command(args)
        if result == 0:
            completed_stages.append("answers")
            update_checkpoint(checkpoint_path, "answers", input_hash, completed_stages)
        return result

    # Handle --validate mode
    if args.validate:
        if should_skip_stage(checkpoint, "validate", input_hash):
            print("Skipping validate stage (already completed)")
            return 0
        result = validate_command(args)
        if result == 0:
            completed_stages.append("validate")
            update_checkpoint(checkpoint_path, "validate", input_hash, completed_stages)
        return result

    # Handle --export mode
    if args.export:
        if should_skip_stage(checkpoint, "export", input_hash):
            print("Skipping export stage (already completed)")
            return 0
        result = export_command(args)
        if result == 0:
            completed_stages.append("export")
            update_checkpoint(checkpoint_path, "export", input_hash, completed_stages)
            # All stages done - clean up checkpoint
            if set(completed_stages) >= {"questions", "index", "answers", "validate", "export"}:
                delete_checkpoint(checkpoint_path)
                print("All stages complete - checkpoint removed")
        return result

    # Default mode: Generate questions
    # Check if we should skip questions stage
    if should_skip_stage(checkpoint, "questions", input_hash):
        print("Skipping questions stage (already completed)")
        return 0

    # Validate input directory
    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        return 1

    # Load personas
    try:
        personas = load_personas(args.personas)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error loading personas: {e}")
        return 1

    print(f"Loaded {len(personas)} personas:")
    for p in personas:
        print(f"  - {p.id}")

    # Single file mode
    if args.file:
        if not args.file.exists():
            print(f"Error: File {args.file} does not exist")
            return 1

        print()
        print(f"Single file mode: {args.file}")

        # Select persona for the document
        persona = select_persona_for_document(args.file, personas)
        print(f"Selected persona: {persona.id}")
        print(f"  - Roll: {persona.roll}")
        print(f"  - Erfarenhet: {persona.erfarenhet}")
        print(f"  - Situation: {persona.situation}")
        print(f"  - Sprakbakgrund: {persona.sprakbakgrund}")
        print()

        # Generate questions
        print("Generating questions...")
        questions = generate_questions_for_document(args.file, persona, delay=0.1)

        if not questions:
            print("No questions generated (check GEMINI_API_KEY)")
            return 1

        print(f"\nGenerated {len(questions)} questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. [{q.question_type}] {q.question}")
            print(f"   Section: {q.section}")
            print(f"   Confidence: {q.confidence:.2f}")
            print()

        return 0

    # Batch mode
    print()
    documents = list(args.input.rglob("*.md"))
    print(f"Found {len(documents)} documents")

    # Apply limit if specified
    if args.limit:
        random.shuffle(documents)  # Randomize for variety when limiting
        documents = documents[:args.limit]
        print(f"Processing {args.limit} documents (limit applied)")

    if not documents:
        print("No markdown documents found")
        return 1

    # Process documents with progress bar
    print()
    questions = process_documents_batch(
        documents=documents,
        personas=personas,
        max_workers=5,
        delay=0.2
    )
    print(f"\nGenerated {len(questions)} questions")

    # Deduplicate
    unique_questions = deduplicate_questions(questions, threshold=0.85)
    removed = len(questions) - len(unique_questions)
    print(f"After deduplication: {len(unique_questions)} unique questions ({removed} duplicates removed)")

    # Write output
    output_file = args.output / "questions.yaml"
    write_questions_yaml(unique_questions, output_file)
    print(f"Saved to {output_file}")

    # Summary by category
    if args.verbose:
        print("\nQuestions by category:")
        from collections import Counter
        category_counts = Counter(q.category for q in unique_questions)
        for category, count in sorted(category_counts.items()):
            print(f"  {category}: {count}")

    # Update checkpoint after successful questions generation
    completed_stages.append("questions")
    update_checkpoint(checkpoint_path, "questions", input_hash, completed_stages)

    return 0


if __name__ == "__main__":
    sys.exit(main())

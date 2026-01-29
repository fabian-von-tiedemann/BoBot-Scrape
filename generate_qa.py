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

    # Handle --build-index mode
    if args.build_index:
        return build_index_command(args)

    # Handle --answers mode
    if args.answers:
        return generate_answers_command(args)

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

    return 0


if __name__ == "__main__":
    sys.exit(main())

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
"""
import argparse
import sys
from pathlib import Path

from src.qa import Persona, load_personas


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs from converted documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Use defaults
  %(prog)s --input converted/           Custom input directory
  %(prog)s --personas config/p.yaml     Custom persona config
  %(prog)s --file converted/doc.md      Single file mode (for testing)
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
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    return parser.parse_args()


def main():
    """Run the QA generation pipeline."""
    args = parse_args()

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

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # TODO: Phase 28+ implementation
    print()
    print(f"Would process {args.input} -> {args.output} with {len(personas)} personas")

    if args.file:
        print(f"Single file mode: {args.file}")

    if args.verbose:
        print()
        print("Verbose mode enabled")

    return 0


if __name__ == "__main__":
    sys.exit(main())

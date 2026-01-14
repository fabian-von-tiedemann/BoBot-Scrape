"""
BoBot-Scrape Document Converter: Transform documents to AI-enriched Markdown

Processes downloaded PDF and Word documents from downloads/ into well-formatted
Markdown files with YAML frontmatter containing AI-generated metadata.

Prerequisites:
    1. Documents downloaded via scrape.py
    2. (Optional) GEMINI_API_KEY in .env for AI metadata generation

Usage:
    .venv/bin/python convert.py [OPTIONS]

Options:
    --input DIR     Source folder with documents (default: downloads/)
    --output DIR    Destination for markdown files (default: converted/)
    --force         Re-convert existing files
    --skip-ai       Skip Gemini metadata generation (faster, no API calls)
    --help          Show this help message

Examples:
    # Convert all documents with AI metadata
    .venv/bin/python convert.py

    # Fast conversion without AI (no API calls)
    .venv/bin/python convert.py --skip-ai

    # Re-convert everything, overwrite existing
    .venv/bin/python convert.py --force

    # Custom input/output directories
    .venv/bin/python convert.py --input my-docs/ --output my-markdown/

Output:
    converted/                    - Base folder for all output
    converted/{category}/         - One folder per source category
    converted/{category}/*.md     - Markdown files with YAML frontmatter
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv

from src.extractors import extract_text
from src.formatters import text_to_markdown
from src.ai import generate_metadata

# Load .env at startup
load_dotenv()


def load_document_metadata(csv_path: Path) -> dict[str, dict[str, str]]:
    """Load category/filename -> metadata mapping from documents.csv.

    Returns a dict mapping category/filename to a dict with:
    - url: source URL
    - category: top-level category name (e.g., "Bemanningsenheten", "Hemtjänst")
    - subcategory: subcategory heading from HTML (e.g., "Frånvaro för timvikarier")
    """
    lookup = {}
    if not csv_path.exists():
        return lookup
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Key uses category (which is the folder name)
            key = f"{row['category']}/{row['filename']}"
            lookup[key] = {
                "url": row['url'],
                "category": row['category'],
                "subcategory": row['subcategory']
            }
    return lookup


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert downloaded documents to Markdown with AI metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Convert all documents with AI metadata
  %(prog)s --skip-ai            Fast conversion without API calls
  %(prog)s --force              Re-convert all files
  %(prog)s --input docs/        Custom input directory
        """
    )
    parser.add_argument(
        "--input",
        default="downloads/",
        help="Source folder with documents (default: downloads/)"
    )
    parser.add_argument(
        "--output",
        default="converted/",
        help="Destination folder for markdown files (default: converted/)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-convert existing files"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip Gemini metadata generation (faster, no API calls)"
    )
    return parser.parse_args()


def create_frontmatter(
    filename: str,
    source_path: str,
    source_url: str = "",
    category: str = "",
    subcategory: str = "",
    updated_date: str = "",
    metadata=None
) -> str:
    """
    Create YAML frontmatter for a markdown document.

    Args:
        filename: Original filename (without extension)
        source_path: Relative path from input directory
        source_url: URL to original document (from documents.csv)
        category: Top-level category name
        subcategory: Subcategory heading
        updated_date: Document update/revision date (YYYY-MM-DD)
        metadata: Optional DocumentMetadata from AI

    Returns:
        YAML frontmatter string including opening and closing ---
    """
    lines = ["---"]
    lines.append(f'title: "{filename}"')
    lines.append(f'source_file: "{source_path}"')
    lines.append(f'source_url: "{source_url}"')
    lines.append(f'category: "{category}"')
    lines.append(f'subcategory: "{subcategory}"')
    lines.append(f'updated_date: "{updated_date}"')

    if metadata:
        lines.append(f"document_type: {metadata.document_type}")
        # Multiline summary
        lines.append("summary: |")
        for line in metadata.summary.split('\n'):
            lines.append(f"  {line}")
        # Keywords as list
        lines.append("keywords:")
        for kw in metadata.keywords:
            lines.append(f"  - \"{kw}\"")
        # Topics as list
        lines.append("topics:")
        for topic in metadata.topics:
            lines.append(f"  - \"{topic}\"")

    lines.append("---")
    return "\n".join(lines)


def process_file(
    input_path: Path,
    output_path: Path,
    input_base: Path,
    metadata_lookup: dict[str, dict[str, str]],
    skip_ai: bool = False
) -> tuple[bool, str]:
    """
    Process a single document file.

    Args:
        input_path: Path to source document
        output_path: Path for output markdown file
        input_base: Base input directory (for relative path calculation)
        metadata_lookup: Mapping of category/filename to metadata (url, verksamhet, rutin)
        skip_ai: Whether to skip AI metadata generation

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Extract text
    text = extract_text(str(input_path))
    if not text:
        return False, "text extraction failed"

    # Convert to markdown
    markdown_body = text_to_markdown(text)
    if not markdown_body:
        return False, "markdown formatting failed"

    # Generate AI metadata (unless skipped)
    metadata = None
    if not skip_ai:
        metadata = generate_metadata(text)
        # If AI fails, we continue without metadata

    # Create frontmatter with decoded filename and document metadata
    source_path = str(input_path.relative_to(input_base))
    decoded_filename = unquote(input_path.stem)
    doc_metadata = metadata_lookup.get(source_path, {})
    source_url = doc_metadata.get("url", "")
    category = doc_metadata.get("category", "")
    subcategory = doc_metadata.get("subcategory", "")
    updated_date = metadata.updated_date if metadata else ""
    frontmatter = create_frontmatter(
        decoded_filename, source_path, source_url, category, subcategory, updated_date, metadata
    )

    # Combine and write
    full_content = f"{frontmatter}\n\n{markdown_body}"

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    output_path.write_text(full_content, encoding="utf-8")

    return True, "converted"


def main():
    """Convert downloaded documents to markdown with AI metadata."""
    args = parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    force = args.force
    skip_ai = args.skip_ai

    # Print mode
    if skip_ai:
        print("Mode: CONVERT (skip AI metadata)")
    elif force:
        print("Mode: FORCE CONVERT (re-convert all files, with AI)")
    else:
        print("Mode: CONVERT (skip existing files, with AI)")
    print()

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    # Load document metadata from documents.csv
    metadata_lookup = load_document_metadata(input_dir / "documents.csv")
    if metadata_lookup:
        print(f"Loaded metadata for {len(metadata_lookup)} documents from documents.csv")
    print()

    # Find all documents
    document_extensions = {'.pdf', '.docx'}
    documents = []
    for ext in document_extensions:
        documents.extend(input_dir.rglob(f"*{ext}"))

    # Sort for consistent order
    documents = sorted(documents)

    print(f"Found {len(documents)} documents in {input_dir}")
    print()

    # Process documents
    converted_count = 0
    skipped_count = 0
    failed_count = 0
    failed_files = []

    for doc_path in documents:
        # Calculate output path with decoded filename
        relative_path = doc_path.relative_to(input_dir)
        decoded_stem = unquote(relative_path.stem)
        output_path = output_dir / relative_path.parent / f"{decoded_stem}.md"

        # Skip if exists (unless --force)
        if output_path.exists() and not force:
            skipped_count += 1
            print(f"Skipped (exists): {relative_path}")
            continue

        # Process file
        try:
            success, message = process_file(
                doc_path, output_path, input_dir, metadata_lookup, skip_ai
            )
            if success:
                converted_count += 1
                print(f"Converted: {relative_path}")
            else:
                failed_count += 1
                failed_files.append((relative_path, message))
                print(f"Failed: {relative_path} ({message})")
        except Exception as e:
            failed_count += 1
            failed_files.append((relative_path, str(e)))
            print(f"Failed: {relative_path} ({e})")

    # Print summary
    print()
    print("=" * 60)
    print("Conversion Summary")
    print("=" * 60)
    print(f"Converted: {converted_count}")
    print(f"Skipped:   {skipped_count}")
    print(f"Failed:    {failed_count}")
    print(f"Total:     {len(documents)}")

    if failed_files:
        print()
        print(f"Failed files ({len(failed_files)}):")
        for path, reason in failed_files[:10]:
            print(f"  - {path}: {reason}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")

    print("=" * 60)


if __name__ == "__main__":
    main()

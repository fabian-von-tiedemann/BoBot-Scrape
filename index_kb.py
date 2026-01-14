#!/usr/bin/env python3
"""Knowledge Base indexer CLI.

Creates index files for each verksamhet folder in the knowledge base.
"""

import argparse
import sys
import time
from pathlib import Path

from src.indexer import index_folder, write_index


def main():
    parser = argparse.ArgumentParser(
        description='Index knowledge base documents and generate index files for each verksamhet.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python index_kb.py                              # Use default paths
  python index_kb.py --input converted --output indexes
  python index_kb.py -i ./my_docs -o ./my_indexes
        """
    )
    parser.add_argument(
        '--input', '-i',
        default='./converted',
        help='Input directory containing verksamhet folders (default: ./converted)'
    )
    parser.add_argument(
        '--output', '-o',
        default='./indexes',
        help='Output directory for index files (default: ./indexes)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Print verbose output'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    # Validate input directory
    if not input_path.exists():
        print(f"Error: Input directory does not exist: {input_path}")
        sys.exit(1)

    if not input_path.is_dir():
        print(f"Error: Input path is not a directory: {input_path}")
        sys.exit(1)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all verksamhet folders (subdirectories)
    verksamhet_folders = sorted([
        d for d in input_path.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ])

    if not verksamhet_folders:
        print(f"No verksamhet folders found in {input_path}")
        sys.exit(1)

    print(f"Indexing {len(verksamhet_folders)} verksamheter from {input_path}")
    print(f"Output directory: {output_path}")
    print()

    start_time = time.time()
    total_documents = 0
    successful_indexes = 0

    for folder in verksamhet_folders:
        print(f"Processing: {folder.name}...", end=' ')

        try:
            index = index_folder(folder)
            output_file = output_path / f"{folder.name}-INDEX.md"
            write_index(index, output_file)

            print(f"{index.document_count} documents")
            if args.verbose:
                print(f"  Types: {dict(index.document_types)}")
                print(f"  Subcategories: {len(index.subcategories)}")
                print(f"  Keywords: {len(index.all_keywords)}")
                print(f"  Topics: {len(index.all_topics)}")

            total_documents += index.document_count
            successful_indexes += 1

        except Exception as e:
            print(f"ERROR: {e}")
            continue

    elapsed = time.time() - start_time

    print()
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    print(f"Verksamheter indexed: {successful_indexes}/{len(verksamhet_folders)}")
    print(f"Total documents: {total_documents}")
    print(f"Time elapsed: {elapsed:.2f}s")
    print(f"Index files created in: {output_path}")


if __name__ == '__main__':
    main()

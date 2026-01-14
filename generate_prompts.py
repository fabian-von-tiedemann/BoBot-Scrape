#!/usr/bin/env python3
"""
Generate system prompts for AI assistants based on document index files.

Usage:
    python generate_prompts.py --input indexes --output prompts --verbose
"""
import argparse
from pathlib import Path

from src.prompt_generator import (
    read_index_file,
    generate_system_prompt,
    format_prompt
)


def main():
    parser = argparse.ArgumentParser(
        description='Generate system prompts from document index files'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=Path('./indexes'),
        help='Input directory with index files (default: ./indexes)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('./prompts'),
        help='Output directory for prompts (default: ./prompts)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    # Validate input directory
    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        return 1

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Find all index files
    index_files = sorted(args.input.glob('*-INDEX.md'))

    if not index_files:
        print(f"No *-INDEX.md files found in {args.input}")
        return 1

    if args.verbose:
        print(f"Found {len(index_files)} index files in {args.input}")
        print()

    generated_count = 0
    skipped_count = 0

    for index_file in index_files:
        # Extract verksamhet name from filename (e.g., "Hemtjänst" from "Hemtjänst-INDEX.md")
        verksamhet_name = index_file.stem.replace('-INDEX', '')

        print(f"Processing {verksamhet_name}...", end=' ', flush=True)

        try:
            # Read index content
            index_content = read_index_file(index_file)

            if not index_content.strip():
                print("skipped (empty file)")
                skipped_count += 1
                continue

            # Generate system prompt
            system_prompt = generate_system_prompt(index_content)

            if system_prompt is None:
                print("skipped (generation failed)")
                skipped_count += 1
                continue

            # Format and write output
            prompt_content = format_prompt(system_prompt)
            output_file = args.output / f"{verksamhet_name}-PROMPT.md"
            output_file.write_text(prompt_content, encoding='utf-8')

            print("done")
            generated_count += 1

            if args.verbose:
                print(f"  → {output_file}")
                print(f"  Key areas: {len(system_prompt.key_areas)}")
                print()

        except Exception as e:
            print(f"error ({e})")
            skipped_count += 1
            continue

    print()
    print(f"Generated {generated_count} prompts in {args.output}")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} files")

    return 0


if __name__ == '__main__':
    exit(main())

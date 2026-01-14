#!/usr/bin/env python3
"""
Combine general and specific system prompts into complete prompts.

Usage:
    python combine_prompts.py --general prompts/GENERAL.md --input prompts --output prompts/combined
"""
import argparse
from pathlib import Path

from src.prompt_combiner import (
    load_general_prompt,
    load_specific_prompt,
    combine_prompts,
    write_combined,
    get_combined_filename
)


def main():
    parser = argparse.ArgumentParser(
        description='Combine general and specific system prompts'
    )
    parser.add_argument(
        '--general', '-g',
        type=Path,
        default=Path('./prompts/GENERAL.md'),
        help='Path to general prompt file (default: ./prompts/GENERAL.md)'
    )
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=Path('./prompts'),
        help='Input directory with specific prompts (default: ./prompts)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('./prompts/combined'),
        help='Output directory for combined prompts (default: ./prompts/combined)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )

    args = parser.parse_args()

    # Validate general prompt exists
    if not args.general.exists():
        print(f"Error: General prompt file {args.general} does not exist")
        return 1

    # Validate input directory
    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        return 1

    # Load general prompt
    general_content = load_general_prompt(args.general)
    if args.verbose:
        print(f"Loaded general prompt from {args.general}")

    # Find all specific prompt files
    specific_files = sorted(args.input.glob('*-PROMPT.md'))

    if not specific_files:
        print(f"No *-PROMPT.md files found in {args.input}")
        return 1

    print(f"Found {len(specific_files)} specific prompts in {args.input}")
    print()

    combined_count = 0

    for specific_file in specific_files:
        # Get verksamhet name from filename
        verksamhet_name = specific_file.stem.replace('-PROMPT', '')

        print(f"Combining {verksamhet_name}...", end=' ', flush=True)

        try:
            # Load specific prompt
            specific_content = load_specific_prompt(specific_file)

            # Combine prompts
            combined_content = combine_prompts(general_content, specific_content)

            # Get output filename and write
            output_filename = get_combined_filename(specific_file)
            output_path = args.output / output_filename
            write_combined(combined_content, output_path)

            print("done")
            combined_count += 1

            if args.verbose:
                print(f"  → {output_path}")
                print()

        except Exception as e:
            print(f"error ({e})")
            continue

    print()
    print(f"Combined {combined_count} prompts in {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())

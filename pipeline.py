#!/usr/bin/env python3
"""
BoBot-Scrape Pipeline Runner: Unified CLI for ETL pipeline

Orchestrates all stages of the document processing pipeline:
1. Scrape - Download documents from Botkyrka intranet
2. Convert - Transform documents to AI-enriched Markdown
3. Index - Create index files for each verksamhet
4. Generate - Create system prompts from indexes
5. Combine - Merge general and specific prompts

All outputs are written to timestamped run directories for version control.

Prerequisites:
    1. For scraping: Chrome running with --remote-debugging-port=9222
    2. For AI metadata: GEMINI_API_KEY in .env
    3. For prompts: prompts/GENERAL.md exists

Usage:
    python pipeline.py [OPTIONS]

Options:
    --run-dir DIR   Custom run directory (default: auto-generated timestamp)
    --skip-scrape   Skip download stage (use existing downloads/)
    --skip-ai       Skip AI metadata generation in convert stage
    --force         Re-process everything (passed to scrape.py and convert.py)
    --help          Show this help message

Examples:
    # Full pipeline (requires Chrome with debug port)
    python pipeline.py

    # Skip scraping, use existing downloads
    python pipeline.py --skip-scrape

    # Fast run without AI
    python pipeline.py --skip-scrape --skip-ai

    # Re-process all documents
    python pipeline.py --skip-scrape --force

Output:
    runs/YYYY-MM-DD-HHMM/           - Timestamped run directory
    runs/YYYY-MM-DD-HHMM/downloads/ - Raw PDF/Word files (if scraping)
    runs/YYYY-MM-DD-HHMM/converted/ - Markdown files with AI metadata
    runs/YYYY-MM-DD-HHMM/indexes/   - Verksamhet index files
    runs/YYYY-MM-DD-HHMM/prompts/   - Generated prompts
    runs/YYYY-MM-DD-HHMM/prompts/combined/ - Combined system prompts
"""

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the complete document processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                      Full pipeline (requires Chrome)
  %(prog)s --skip-scrape        Use existing downloads/
  %(prog)s --skip-scrape --skip-ai   Fast run without AI
  %(prog)s --force              Re-process all documents
        """
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        default=None,
        help="Custom run directory (default: runs/YYYY-MM-DD-HHMM)"
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip download stage (use existing downloads/)"
    )
    parser.add_argument(
        "--skip-ai",
        action="store_true",
        help="Skip AI metadata generation in convert stage"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-process everything (passed to scrape.py and convert.py)"
    )
    return parser.parse_args()


def create_manifest(csv_path: Path, run_id: str) -> dict:
    """
    Create manifest structure from documents.csv.

    Args:
        csv_path: Path to documents.csv file
        run_id: Identifier for this run (timestamp)

    Returns:
        Manifest dict with document URLs and hashes
    """
    manifest = {
        "run_id": run_id,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "document_count": 0,
        "documents": {}
    }

    if not csv_path.exists():
        return manifest

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Key is category/filename (relative path)
            key = f"{row['category']}/{row['filename']}"
            url = row['url']
            manifest["documents"][key] = {
                "url": url,
                "url_hash": hashlib.md5(url.encode()).hexdigest(),
                "category": row['category'],
                "subcategory": row.get('subcategory', '')
            }

    manifest["document_count"] = len(manifest["documents"])
    return manifest


def save_manifest(manifest: dict, run_dir: Path) -> None:
    """
    Write manifest.json to run directory.

    Args:
        manifest: Manifest dict to save
        run_dir: Run directory path
    """
    manifest_path = run_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Manifest saved: {manifest_path}")
    print(f"  - {manifest['document_count']} documents tracked")


def load_manifest(run_dir: Path) -> dict | None:
    """
    Load manifest.json from run directory.

    Args:
        run_dir: Run directory path

    Returns:
        Manifest dict or None if not found
    """
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return None

    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def run_stage(name: str, cmd: list[str], cwd: str = None) -> tuple[bool, float]:
    """
    Run a pipeline stage and capture timing.

    Args:
        name: Stage name for display
        cmd: Command to run as list of strings
        cwd: Working directory (optional)

    Returns:
        Tuple of (success: bool, duration_seconds: float)
    """
    print()
    print("=" * 60)
    print(f"STAGE: {name}")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print()

    start_time = time.time()

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,  # Don't raise on non-zero exit
        )
        duration = time.time() - start_time

        if result.returncode != 0:
            print()
            print(f"ERROR: Stage '{name}' failed with exit code {result.returncode}")
            return False, duration

        print()
        print(f"Stage '{name}' completed in {duration:.1f}s")
        return True, duration

    except Exception as e:
        duration = time.time() - start_time
        print()
        print(f"ERROR: Stage '{name}' failed with exception: {e}")
        return False, duration


def main():
    """Run the complete pipeline."""
    args = parse_args()
    pipeline_start = time.time()

    # Generate run directory name
    if args.run_dir:
        run_dir = Path(args.run_dir)
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        run_dir = Path("runs") / timestamp

    # Create run directory structure
    run_dir.mkdir(parents=True, exist_ok=True)
    downloads_dir = run_dir / "downloads"
    converted_dir = run_dir / "converted"
    indexes_dir = run_dir / "indexes"
    prompts_dir = run_dir / "prompts"
    combined_dir = prompts_dir / "combined"

    # Print header
    print()
    print("=" * 60)
    print("BOBOT-SCRAPE PIPELINE")
    print("=" * 60)
    print()
    print(f"Run directory: {run_dir}")
    print()
    print("Options:")
    print(f"  --skip-scrape: {args.skip_scrape}")
    print(f"  --skip-ai:     {args.skip_ai}")
    print(f"  --force:       {args.force}")
    print()

    # Determine input directory for convert stage
    if args.skip_scrape:
        # Use existing downloads/ directory
        input_dir = Path("downloads")
        if not input_dir.exists():
            print(f"ERROR: downloads/ directory not found (required with --skip-scrape)")
            sys.exit(1)
        print(f"Using existing downloads from: {input_dir}")
    else:
        # Scrape will create downloads in run directory
        input_dir = downloads_dir
        downloads_dir.mkdir(parents=True, exist_ok=True)

    stage_times = {}

    # Use sys.executable to ensure we use the same Python interpreter
    python_exe = sys.executable

    # ========== STAGE 1: Scrape (optional) ==========
    if not args.skip_scrape:
        # Note: scrape.py currently writes to downloads/ in current directory
        # We would need to modify scrape.py to support --output flag for run directories
        # For now, we skip this stage when --skip-scrape is used
        cmd = [python_exe, "scrape.py"]
        if args.force:
            cmd.append("--force")

        success, duration = run_stage("Scrape (download documents)", cmd)
        stage_times["scrape"] = duration

        if not success:
            print()
            print("Pipeline failed at scrape stage")
            sys.exit(1)

        # Copy documents.csv to run directory if needed
        # Note: scrape.py outputs to downloads/, not run_dir/downloads/
        # This is a known limitation - would need scrape.py modification
    else:
        print("Skipping scrape stage (--skip-scrape)")
        stage_times["scrape"] = 0

    # Create manifest from documents.csv
    csv_path = input_dir / "documents.csv"
    run_id = run_dir.name  # Use timestamp directory name as run_id
    manifest = create_manifest(csv_path, run_id)
    save_manifest(manifest, run_dir)
    print()

    # ========== STAGE 2: Convert ==========
    cmd = [
        python_exe, "convert.py",
        "--input", str(input_dir),
        "--output", str(converted_dir)
    ]
    if args.skip_ai:
        cmd.append("--skip-ai")
    if args.force:
        cmd.append("--force")

    success, duration = run_stage("Convert (documents to markdown)", cmd)
    stage_times["convert"] = duration

    if not success:
        print()
        print("Pipeline failed at convert stage")
        sys.exit(1)

    # ========== STAGE 3: Index ==========
    cmd = [
        python_exe, "index_kb.py",
        "--input", str(converted_dir),
        "--output", str(indexes_dir)
    ]

    success, duration = run_stage("Index (create verksamhet indexes)", cmd)
    stage_times["index"] = duration

    if not success:
        print()
        print("Pipeline failed at index stage")
        sys.exit(1)

    # ========== STAGE 4: Generate Prompts ==========
    cmd = [
        python_exe, "generate_prompts.py",
        "--input", str(indexes_dir),
        "--output", str(prompts_dir)
    ]

    success, duration = run_stage("Generate (create system prompts)", cmd)
    stage_times["generate"] = duration

    if not success:
        print()
        print("Pipeline failed at generate stage")
        sys.exit(1)

    # ========== STAGE 5: Combine Prompts ==========
    # General prompt comes from root prompts/ directory
    general_prompt = Path("prompts/GENERAL.md")
    if not general_prompt.exists():
        print()
        print(f"WARNING: {general_prompt} not found, skipping combine stage")
        stage_times["combine"] = 0
    else:
        cmd = [
            python_exe, "combine_prompts.py",
            "--general", str(general_prompt),
            "--input", str(prompts_dir),
            "--output", str(combined_dir)
        ]

        success, duration = run_stage("Combine (merge general + specific prompts)", cmd)
        stage_times["combine"] = duration

        if not success:
            print()
            print("Pipeline failed at combine stage")
            sys.exit(1)

    # ========== SUMMARY ==========
    total_time = time.time() - pipeline_start

    print()
    print("=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print()
    print(f"Run directory: {run_dir}")
    print()
    print("Stage timings:")
    for stage, duration in stage_times.items():
        if duration > 0:
            print(f"  {stage:12}: {duration:6.1f}s")
    print(f"  {'TOTAL':12}: {total_time:6.1f}s")
    print()
    print("Output directories:")
    if converted_dir.exists():
        converted_count = len(list(converted_dir.rglob("*.md")))
        print(f"  {converted_dir}: {converted_count} markdown files")
    if indexes_dir.exists():
        index_count = len(list(indexes_dir.glob("*-INDEX.md")))
        print(f"  {indexes_dir}: {index_count} index files")
    if prompts_dir.exists():
        prompt_count = len(list(prompts_dir.glob("*-PROMPT.md")))
        print(f"  {prompts_dir}: {prompt_count} prompt files")
    if combined_dir.exists():
        combined_count = len(list(combined_dir.glob("*-COMBINED.md")))
        print(f"  {combined_dir}: {combined_count} combined prompts")
    print()


if __name__ == "__main__":
    main()

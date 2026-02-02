"""
Checkpoint module for resumable QA generation.

Provides file-level checkpointing to track which stages have completed
and allow resumption after interruption.
"""
import hashlib
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


StageType = Literal["questions", "index", "answers", "validate", "export"]


class Checkpoint(BaseModel):
    """Checkpoint state for QA generation pipeline."""

    stage: StageType
    input_hash: str  # MD5 of input directory state
    completed_stages: list[str]  # Stages already done
    timestamp: str  # ISO format


def compute_file_hash(path: Path) -> str:
    """
    Compute MD5 hash of file for change detection.

    Args:
        path: Path to file

    Returns:
        MD5 hex digest of file contents
    """
    hasher = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_dir_hash(dir_path: Path, pattern: str = "*.md") -> str:
    """
    Compute hash of directory contents (sorted file list + sizes).

    This provides a fast way to detect if directory contents changed
    without hashing all file contents.

    Args:
        dir_path: Directory to hash
        pattern: Glob pattern for files to include

    Returns:
        MD5 hex digest of directory state
    """
    hasher = hashlib.md5()

    # Get sorted list of files matching pattern
    files = sorted(dir_path.rglob(pattern))

    for file_path in files:
        # Include relative path and file size in hash
        rel_path = file_path.relative_to(dir_path)
        file_size = file_path.stat().st_size
        hasher.update(f"{rel_path}:{file_size}\n".encode())

    return hasher.hexdigest()


def save_checkpoint(checkpoint_path: Path, checkpoint: Checkpoint) -> None:
    """
    Save checkpoint atomically using temp file + rename.

    Args:
        checkpoint_path: Path to save checkpoint file
        checkpoint: Checkpoint state to save
    """
    # Ensure parent directory exists
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first for atomic operation
    temp_fd, temp_path = tempfile.mkstemp(
        suffix='.json',
        dir=checkpoint_path.parent
    )

    try:
        with open(temp_fd, 'w', encoding='utf-8') as f:
            json.dump(checkpoint.model_dump(), f, indent=2, ensure_ascii=False)

        # Atomic rename
        Path(temp_path).rename(checkpoint_path)
    except Exception:
        # Clean up temp file on error
        try:
            Path(temp_path).unlink()
        except OSError:
            pass
        raise


def load_checkpoint(checkpoint_path: Path) -> Checkpoint | None:
    """
    Load checkpoint if exists and valid.

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Checkpoint if valid, None otherwise
    """
    if not checkpoint_path.exists():
        return None

    try:
        with open(checkpoint_path, encoding='utf-8') as f:
            data = json.load(f)
        return Checkpoint(**data)
    except (json.JSONDecodeError, ValueError, KeyError):
        # Invalid checkpoint file - treat as no checkpoint
        return None


def should_skip_stage(
    checkpoint: Checkpoint | None,
    stage: str,
    input_hash: str
) -> bool:
    """
    Check if stage can be skipped (already completed with same input).

    A stage can be skipped if:
    1. A valid checkpoint exists
    2. The input hash matches (no source changes)
    3. The stage is in the completed_stages list

    Args:
        checkpoint: Current checkpoint state (or None)
        stage: Stage name to check
        input_hash: Current input directory hash

    Returns:
        True if stage can be skipped
    """
    if checkpoint is None:
        return False

    # Input changed - can't skip anything
    if checkpoint.input_hash != input_hash:
        return False

    # Check if stage already completed
    return stage in checkpoint.completed_stages


def delete_checkpoint(checkpoint_path: Path) -> None:
    """
    Delete checkpoint file after successful completion.

    Args:
        checkpoint_path: Path to checkpoint file to delete
    """
    if checkpoint_path.exists():
        checkpoint_path.unlink()

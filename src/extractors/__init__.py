"""
Text extraction module for BoBot-Scrape.

Extracts text from PDF and Word documents.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text(filepath: str) -> Optional[str]:
    """
    Extract text content from a file.

    Auto-detects file type from extension and dispatches to appropriate extractor.

    Args:
        filepath: Path to the file to extract text from

    Returns:
        Extracted text content, or None if extraction fails or file type unsupported
    """
    path = Path(filepath)

    if not path.exists():
        logger.warning(f"File not found: {filepath}")
        return None

    extension = path.suffix.lower()

    if extension == '.pdf':
        from .pdf import extract_pdf
        return extract_pdf(filepath)
    elif extension == '.docx':
        from .word import extract_word
        return extract_word(filepath)
    elif extension == '.doc':
        logger.warning(f"Legacy .doc format not supported: {filepath}")
        return None
    else:
        logger.warning(f"Unsupported file type '{extension}': {filepath}")
        return None


__all__ = ['extract_text']

"""
Text formatting module for BoBot-Scrape.

Converts extracted text to structured Markdown format.
"""
import logging
from typing import Optional

from .markdown import format_to_markdown

logger = logging.getLogger(__name__)


def text_to_markdown(text: Optional[str]) -> str:
    """
    Convert extracted text to well-structured Markdown.

    Detects Swedish rutindokument structure and formats accordingly:
    - Document titles as # headings
    - Section names as ## headings
    - Bullet points as Markdown lists
    - Tables as Markdown tables

    Args:
        text: Raw text content (typically from extract_text())

    Returns:
        Formatted Markdown string, or empty string if input is None/empty
    """
    if not text:
        return ""

    return format_to_markdown(text)


__all__ = ['text_to_markdown']

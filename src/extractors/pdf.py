"""
PDF text extraction using PyMuPDF (fitz).
"""
import logging
from typing import Optional

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


def extract_pdf(filepath: str) -> Optional[str]:
    """
    Extract text from a PDF file.

    Args:
        filepath: Path to the PDF file

    Returns:
        Extracted text content, or None if extraction fails
    """
    try:
        doc = fitz.open(filepath)
    except Exception as e:
        logger.warning(f"Failed to open PDF '{filepath}': {e}")
        return None

    try:
        pages = []
        for page_num, page in enumerate(doc):
            try:
                text = page.get_text()
                if text:
                    pages.append(text)
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num} in '{filepath}': {e}")
                continue

        doc.close()

        if not pages:
            logger.warning(f"No text extracted from PDF '{filepath}'")
            return None

        return "\n\n".join(pages)

    except Exception as e:
        logger.warning(f"Error processing PDF '{filepath}': {e}")
        doc.close()
        return None

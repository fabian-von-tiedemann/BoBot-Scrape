"""
Gemini-powered metadata generation for Swedish municipal documents.
"""
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / '.env')

logger = logging.getLogger(__name__)


class DocumentMetadata(BaseModel):
    """Structured metadata for a document."""
    summary: str  # 2-3 sentence summary
    keywords: list[str]  # 5-10 relevant keywords
    topics: list[str]  # 2-4 topic categories
    document_type: str  # rutin, policy, instruktion, etc.
    updated_date: str = ""  # YYYY-MM-DD format, or empty if not found


def generate_metadata(
    text: str,
    delay: float = 0.1
) -> Optional[DocumentMetadata]:
    """
    Generate metadata for a document using Gemini 3 Flash Preview.

    Args:
        text: Document text content to analyze
        delay: Optional delay in seconds after API call (rate limit awareness)

    Returns:
        DocumentMetadata with summary, keywords, topics, and document_type,
        or None if generation fails
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set - cannot generate metadata")
        return None

    if not text or not text.strip():
        logger.warning("Empty text provided - cannot generate metadata")
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = """Analyze this Swedish municipal document and extract metadata.
Respond with:
- summary: A 2-3 sentence summary in Swedish
- keywords: 5-10 relevant Swedish keywords
- topics: 2-4 topic categories in Swedish
- document_type: One of: rutin, policy, instruktion, riktlinje, handbok, blankett, other
- updated_date: The document's update/revision date in YYYY-MM-DD format (look for 'Uppdaterad', 'Senast ändrad', 'Reviderad', 'Gäller från', etc.), or empty string if not found

Document text:

"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt + text,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DocumentMetadata,
            )
        )

        # Optional delay for rate limiting
        if delay > 0:
            time.sleep(delay)

        # Log token usage if available
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            logger.debug(
                f"Gemini tokens - prompt: {response.usage_metadata.prompt_token_count}, "
                f"response: {response.usage_metadata.candidates_token_count}"
            )

        return response.parsed

    except ImportError as e:
        logger.error(f"google-genai package not installed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Gemini API error: {e}")
        return None


def batch_generate_metadata(
    texts: list[str],
    max_workers: int = 10,
    delay: float = 0.05
) -> list[Optional[DocumentMetadata]]:
    """
    Generate metadata for multiple documents in parallel using Gemini.

    Args:
        texts: List of document text contents to analyze
        max_workers: Maximum number of parallel API calls (default 10 for rate limits)
        delay: Delay in seconds after each API call (rate limit awareness)

    Returns:
        List of DocumentMetadata (or None for failures), in same order as input texts
    """
    if not texts:
        return []

    logger.info(f"Batch processing {len(texts)} documents with {max_workers} workers")

    def process_single(text: str) -> Optional[DocumentMetadata]:
        """Wrapper for single text processing."""
        return generate_metadata(text, delay=delay)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single, texts))

    success_count = sum(1 for r in results if r is not None)
    logger.info(f"Batch complete: {success_count}/{len(texts)} successful")

    return results

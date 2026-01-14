"""
Gemini-powered metadata generation for Swedish municipal documents.
"""
import os
import logging
import time
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class DocumentMetadata(BaseModel):
    """Structured metadata for a document."""
    summary: str  # 2-3 sentence summary
    keywords: list[str]  # 5-10 relevant keywords
    topics: list[str]  # 2-4 topic categories
    document_type: str  # rutin, policy, instruktion, etc.


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

Document text:

"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
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

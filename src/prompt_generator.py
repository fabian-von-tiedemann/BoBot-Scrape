"""
System prompt generator for Swedish municipal AI assistants.

Uses Gemini to generate unit-specific system prompts based on document index files.
"""
import os
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / '.env')

logger = logging.getLogger(__name__)


class SystemPrompt(BaseModel):
    """Structured system prompt for a verksamhet (business unit)."""
    verksamhet: str  # Unit name
    introduction: str  # 2-3 sentences about the unit's mission
    key_areas: list[str]  # 5-8 main areas based on subcategories/topics
    document_types_summary: str  # Summary of document types available
    guidance: str  # How the AI should use the knowledge


def read_index_file(path: Path) -> str:
    """Read index file content.

    Args:
        path: Path to the index file

    Returns:
        File content as string
    """
    return path.read_text(encoding='utf-8')


def generate_system_prompt(index_content: str) -> Optional[SystemPrompt]:
    """Generate a structured system prompt from index content using Gemini.

    Args:
        index_content: Content of the index file

    Returns:
        SystemPrompt with verksamhet-specific context, or None if generation fails
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.warning("GEMINI_API_KEY not set - cannot generate system prompt")
        return None

    if not index_content or not index_content.strip():
        logger.warning("Empty index content provided")
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = """Du är expert på att skapa systemprompts för AI-assistenter inom svensk kommunal verksamhet.

Baserat på detta index-dokument, skapa en systemprompt för en AI-assistent som ska hjälpa anställda inom denna verksamhet.

Returna:
- verksamhet: Enhetens namn (extrahera från dokumentet)
- introduction: 2-3 meningar på svenska om enhetens uppdrag och syfte
- key_areas: 5-8 huvudområden baserat på subcategories och topics i indexet
- document_types_summary: En kort sammanfattning av vilka typer av dokument som finns (rutiner, instruktioner, blanketter etc.)
- guidance: Vägledning på svenska för hur AI-assistenten ska använda kunskapen för att hjälpa personalen

Index-dokument:

"""

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt + index_content,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SystemPrompt,
            )
        )

        return response.parsed

    except ImportError as e:
        logger.error(f"google-genai package not installed: {e}")
        return None
    except Exception as e:
        logger.warning(f"Gemini API error: {e}")
        return None


def format_prompt(prompt: SystemPrompt) -> str:
    """Format a SystemPrompt to a markdown string.

    Args:
        prompt: The SystemPrompt to format

    Returns:
        Formatted markdown string
    """
    lines = []

    lines.append(f"# Systemprompt: {prompt.verksamhet}")
    lines.append("")
    lines.append("## Introduktion")
    lines.append("")
    lines.append(prompt.introduction)
    lines.append("")
    lines.append("## Huvudområden")
    lines.append("")
    for area in prompt.key_areas:
        lines.append(f"- {area}")
    lines.append("")
    lines.append("## Dokumenttyper")
    lines.append("")
    lines.append(prompt.document_types_summary)
    lines.append("")
    lines.append("## Vägledning")
    lines.append("")
    lines.append(prompt.guidance)
    lines.append("")

    return '\n'.join(lines)

"""
Prompt combiner for combining general and specific system prompts.

Combines the general system prompt (GENERAL.md) with verksamhet-specific prompts
to create complete combined prompts for each unit.
"""
from pathlib import Path
from typing import Optional


def load_general_prompt(path: Path) -> str:
    """Load the general system prompt.

    Args:
        path: Path to the general prompt file (GENERAL.md)

    Returns:
        Content of the general prompt

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    return path.read_text(encoding='utf-8')


def load_specific_prompt(path: Path) -> str:
    """Load a verksamhet-specific prompt.

    Args:
        path: Path to the specific prompt file (*-PROMPT.md)

    Returns:
        Content of the specific prompt

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    return path.read_text(encoding='utf-8')


def combine_prompts(general: str, specific: str) -> str:
    """Combine general and specific prompts into one complete prompt.

    The combined prompt places the general content first, followed by
    the specific content with a clear separator.

    Args:
        general: Content of the general prompt
        specific: Content of the specific prompt

    Returns:
        Combined prompt content
    """
    # Strip trailing whitespace from both
    general = general.rstrip()
    specific = specific.rstrip()

    # Combine with separator
    combined = f"""{general}

---

# Verksamhetsspecifik information

{specific}
"""
    return combined


def write_combined(content: str, path: Path) -> None:
    """Write combined prompt to file.

    Args:
        content: Combined prompt content
        path: Output path for the combined prompt
    """
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def get_combined_filename(specific_path: Path) -> str:
    """Get the combined filename from a specific prompt path.

    Args:
        specific_path: Path to the specific prompt (e.g., Hemtjänst-PROMPT.md)

    Returns:
        Combined filename (e.g., Hemtjänst-COMBINED.md)
    """
    # Replace -PROMPT with -COMBINED
    name = specific_path.stem.replace('-PROMPT', '-COMBINED')
    return f"{name}.md"

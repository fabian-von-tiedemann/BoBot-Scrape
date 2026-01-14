"""
Markdown conversion logic for Swedish rutindokument.
"""
import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# Common Swedish section names (case-insensitive matching)
SECTION_NAMES = [
    'inledning', 'roller och ansvar', 'område', 'utförande',
    'definitioner', 'syfte', 'bakgrund', 'ansvar', 'genomförande',
    'uppföljning', 'dokumentation', 'avvikelser', 'bilagor',
    'allmänt', 'omfattning', 'mål', 'rutiner', 'kontroll'
]

# Metadata field patterns (Swedish document metadata)
METADATA_PATTERNS = [
    r'^Dokumentet är beslutat av[:\s]',
    r'^Dokumentet beslutades den[:\s]',
    r'^Beslutat av[:\s]',
    r'^Beslutades den[:\s]',
    r'^Gäller till[:\s]',
    r'^Gäller från[:\s]',
    r'^Dokumentägare[:\s]',
    r'^Dokumentansvarig[:\s]',
    r'^Version[:\s]',
    r'^Datum[:\s]',
]


def is_metadata_line(line: str) -> bool:
    """Check if line is a metadata field."""
    for pattern in METADATA_PATTERNS:
        if re.match(pattern, line, re.IGNORECASE):
            return True
    return False


def is_all_caps_header(line: str) -> bool:
    """Check if line is an ALL CAPS section header."""
    stripped = line.strip()
    # Must have at least 2 characters and be all uppercase letters/spaces
    if len(stripped) < 2:
        return False
    # Remove common punctuation for check
    clean = re.sub(r'[:\-\s]', '', stripped)
    if not clean:
        return False
    # Must be all uppercase and contain letters
    return clean.isupper() and any(c.isalpha() for c in clean)


def is_section_name(line: str) -> bool:
    """Check if line is a known section name."""
    stripped = line.strip().lower()
    # Remove trailing colon for matching
    stripped = stripped.rstrip(':')
    return stripped in SECTION_NAMES


def is_document_title(line: str) -> bool:
    """Check if line is a document title like 'RUTIN [Name]'."""
    stripped = line.strip()
    # Pattern: starts with RUTIN, POLICY, INSTRUKTION, etc. in all caps
    return bool(re.match(r'^(RUTIN|POLICY|INSTRUKTION|RIKTLINJE)\s+', stripped))


def is_bullet_point(line: str) -> bool:
    """Check if line starts with a bullet character."""
    stripped = line.lstrip()
    return stripped.startswith(('• ', '- ', '* ', '– ', '— '))


def is_numbered_item(line: str) -> bool:
    """Check if line starts with a number and period."""
    stripped = line.lstrip()
    return bool(re.match(r'^\d+\.\s', stripped))


def is_table_row(line: str) -> bool:
    """Check if line appears to be a table row (contains | separators)."""
    return ' | ' in line or line.strip().startswith('|')


def format_bullet_point(line: str) -> str:
    """Convert various bullet formats to Markdown bullet."""
    stripped = line.lstrip()
    # Replace various bullet characters with standard Markdown bullet
    result = re.sub(r'^[•\-\*–—]\s*', '- ', stripped)
    return result


def format_table(lines: List[str], start_idx: int) -> Tuple[List[str], int]:
    """
    Format consecutive table rows as Markdown table.

    Returns formatted lines and the index after the table.
    """
    table_lines = []
    idx = start_idx

    while idx < len(lines) and is_table_row(lines[idx]):
        row = lines[idx].strip()
        # Ensure row starts and ends with |
        if not row.startswith('|'):
            row = '| ' + row
        if not row.endswith('|'):
            row = row + ' |'
        table_lines.append(row)
        idx += 1

    if not table_lines:
        return [], start_idx

    # Add header separator after first row
    if len(table_lines) >= 1:
        # Count columns in first row
        cols = table_lines[0].count('|') - 1
        if cols > 0:
            separator = '|' + '---|' * cols
            table_lines.insert(1, separator)

    return table_lines, idx


def detect_metadata_block_end(lines: List[str]) -> int:
    """
    Detect where the metadata block ends.

    Returns the index of the first non-metadata line after initial metadata.
    """
    in_metadata = False
    metadata_end = 0

    for i, line in enumerate(lines[:15]):  # Check first 15 lines max
        stripped = line.strip()
        if not stripped:
            continue
        if is_metadata_line(stripped):
            in_metadata = True
            metadata_end = i + 1
        elif in_metadata:
            # First non-metadata line after metadata block
            break

    return metadata_end


def format_to_markdown(text: str) -> str:
    """
    Convert extracted text to well-structured Markdown.

    Detects Swedish rutindokument structure:
    - Document titles (RUTIN, POLICY, etc.) -> # heading
    - ALL CAPS section names -> ## heading
    - Known section names -> ## heading
    - Bullet points -> Markdown list items
    - Numbered items -> preserved
    - Tables -> Markdown table format
    - Metadata block -> preserved with --- separator

    Args:
        text: Raw text content

    Returns:
        Formatted Markdown string
    """
    if not text or not text.strip():
        return ""

    lines = text.split('\n')

    # Very short text - minimal formatting
    if len(lines) < 3:
        return text.strip()

    result = []
    metadata_end = detect_metadata_block_end(lines)
    found_title = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty lines - preserve one
        if not stripped:
            # Avoid multiple consecutive blank lines
            if result and result[-1] != '':
                result.append('')
            i += 1
            continue

        # Add metadata separator after metadata block
        if i == metadata_end and metadata_end > 0:
            if result and result[-1] != '---':
                result.append('')
                result.append('---')
                result.append('')

        # Document title (first RUTIN/POLICY line)
        if not found_title and is_document_title(stripped):
            result.append(f'# {stripped}')
            found_title = True
            i += 1
            continue

        # ALL CAPS headers (but not after we've seen the title on same line type)
        if is_all_caps_header(stripped) and len(stripped) < 50:
            # Use # for main titles, ## for sections
            if not found_title:
                result.append(f'# {stripped}')
                found_title = True
            else:
                result.append(f'## {stripped}')
            i += 1
            continue

        # Known section names
        if is_section_name(stripped):
            # Capitalize first letter for heading
            heading = stripped.rstrip(':').capitalize()
            result.append(f'## {heading}')
            i += 1
            continue

        # Table rows
        if is_table_row(stripped):
            table_lines, new_idx = format_table(lines, i)
            result.extend(table_lines)
            i = new_idx
            continue

        # Bullet points
        if is_bullet_point(stripped):
            result.append(format_bullet_point(stripped))
            i += 1
            continue

        # Numbered items - keep as-is
        if is_numbered_item(stripped):
            result.append(stripped)
            i += 1
            continue

        # Regular text line
        result.append(stripped)
        i += 1

    # Join and clean up
    output = '\n'.join(result)

    # Normalize multiple blank lines to single
    output = re.sub(r'\n{3,}', '\n\n', output)

    # Trim trailing whitespace on each line
    output = '\n'.join(line.rstrip() for line in output.split('\n'))

    return output.strip()

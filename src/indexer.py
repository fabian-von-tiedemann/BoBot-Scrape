"""Frontmatter indexer module for knowledge base documents.

Extracts YAML frontmatter from markdown files and creates index summaries
for folders of documents organized by verksamhet (business unit).
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class DocumentSummary:
    """Summary of a single document extracted from its frontmatter."""
    title: str
    file_path: str
    source_url: str = ""
    category: str = ""
    subcategory: str = ""
    updated_date: str = ""
    document_type: str = ""
    summary: str = ""
    keywords: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


@dataclass
class FolderIndex:
    """Index of all documents in a folder (verksamhet)."""
    name: str
    document_count: int
    documents: list[DocumentSummary] = field(default_factory=list)
    subcategories: list[str] = field(default_factory=list)
    all_keywords: list[str] = field(default_factory=list)
    all_topics: list[str] = field(default_factory=list)
    document_types: dict[str, int] = field(default_factory=dict)


def extract_frontmatter(md_file: Path) -> dict:
    """Extract YAML frontmatter from a markdown file.

    Args:
        md_file: Path to the markdown file

    Returns:
        Dictionary containing the frontmatter fields, or empty dict if not found
    """
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  Warning: Could not read {md_file}: {e}")
        return {}

    # Check for frontmatter delimiter
    if not content.startswith('---'):
        return {}

    # Find the closing delimiter
    lines = content.split('\n')
    end_index = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == '---':
            end_index = i
            break

    if end_index == -1:
        return {}

    # Parse YAML content between delimiters
    frontmatter_content = '\n'.join(lines[1:end_index])
    try:
        frontmatter = yaml.safe_load(frontmatter_content)
        return frontmatter if frontmatter else {}
    except yaml.YAMLError as e:
        print(f"  Warning: YAML parse error in {md_file}: {e}")
        return {}


def index_folder(folder: Path) -> FolderIndex:
    """Index all markdown documents in a folder.

    Args:
        folder: Path to the folder to index

    Returns:
        FolderIndex containing summaries of all documents
    """
    documents = []
    all_subcategories = set()
    all_keywords = set()
    all_topics = set()
    document_types: dict[str, int] = {}

    # Find all markdown files in the folder
    md_files = sorted(folder.glob('*.md'))

    for md_file in md_files:
        frontmatter = extract_frontmatter(md_file)

        if not frontmatter:
            # Create minimal summary for files without frontmatter
            doc = DocumentSummary(
                title=md_file.stem,
                file_path=str(md_file)
            )
        else:
            doc = DocumentSummary(
                title=frontmatter.get('title', md_file.stem),
                file_path=str(md_file),
                source_url=frontmatter.get('source_url', ''),
                category=frontmatter.get('category', ''),
                subcategory=frontmatter.get('subcategory', ''),
                updated_date=frontmatter.get('updated_date', ''),
                document_type=frontmatter.get('document_type', ''),
                summary=frontmatter.get('summary', '').strip() if frontmatter.get('summary') else '',
                keywords=frontmatter.get('keywords', []) or [],
                topics=frontmatter.get('topics', []) or []
            )

            # Collect aggregated data
            if doc.subcategory:
                all_subcategories.add(doc.subcategory)
            all_keywords.update(doc.keywords)
            all_topics.update(doc.topics)

            # Count document types
            doc_type = doc.document_type or 'unknown'
            document_types[doc_type] = document_types.get(doc_type, 0) + 1

        documents.append(doc)

    return FolderIndex(
        name=folder.name,
        document_count=len(documents),
        documents=documents,
        subcategories=sorted(all_subcategories),
        all_keywords=sorted(all_keywords),
        all_topics=sorted(all_topics),
        document_types=document_types
    )


def write_index(index: FolderIndex, output_path: Path) -> None:
    """Write a folder index to a markdown file.

    Args:
        index: The FolderIndex to write
        output_path: Path to the output markdown file
    """
    lines = []

    # Header
    lines.append(f"# {index.name} - Document Index")
    lines.append("")
    lines.append(f"**Total Documents:** {index.document_count}")
    lines.append("")

    # Document Types Summary
    if index.document_types:
        lines.append("## Document Types")
        lines.append("")
        for doc_type, count in sorted(index.document_types.items(), key=lambda x: -x[1]):
            lines.append(f"- **{doc_type}:** {count}")
        lines.append("")

    # Subcategories
    if index.subcategories:
        lines.append("## Subcategories")
        lines.append("")
        for subcat in index.subcategories:
            lines.append(f"- {subcat}")
        lines.append("")

    # Topics
    if index.all_topics:
        lines.append("## Topics")
        lines.append("")
        for topic in index.all_topics:
            lines.append(f"- {topic}")
        lines.append("")

    # Keywords
    if index.all_keywords:
        lines.append("## Keywords")
        lines.append("")
        # Join keywords with commas for readability
        lines.append(", ".join(index.all_keywords))
        lines.append("")

    # Document List
    lines.append("## Documents")
    lines.append("")

    for doc in index.documents:
        lines.append(f"### {doc.title}")
        lines.append("")

        # Metadata line
        metadata_parts = []
        if doc.document_type:
            metadata_parts.append(f"**Type:** {doc.document_type}")
        if doc.subcategory:
            metadata_parts.append(f"**Subcategory:** {doc.subcategory}")
        if doc.updated_date:
            metadata_parts.append(f"**Updated:** {doc.updated_date}")

        if metadata_parts:
            lines.append(" | ".join(metadata_parts))
            lines.append("")

        # Summary
        if doc.summary:
            lines.append(doc.summary)
            lines.append("")

        # Keywords for this document
        if doc.keywords:
            lines.append(f"**Keywords:** {', '.join(doc.keywords)}")
            lines.append("")

        # Topics for this document
        if doc.topics:
            lines.append(f"**Topics:** {', '.join(doc.topics)}")
            lines.append("")

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')

"""
HuggingFace-compatible JSONL export for validated QA pairs.

Transforms internal validation output (Swedish field names, nested objects)
to flat JSONL format that works directly with datasets.load_dataset('json', ...).
"""
import json
from pathlib import Path
from typing import Iterator


def transform_to_hf(entry: dict) -> dict:
    """
    Transform a validated QA entry to flat HuggingFace-compatible format.

    Input: validated QA entry from qa_passed.jsonl (has nested validation object)
    Output: flat dict with English field names

    Args:
        entry: Dict with question, answer, persona (nested), validation (nested)

    Returns:
        Flat dict with: question, answer, source, persona, validation_score
    """
    # Extract persona info with graceful defaults
    persona_dict = entry.get("persona", {})
    if isinstance(persona_dict, dict):
        roll = persona_dict.get("roll", "unknown")
        erfarenhet = persona_dict.get("erfarenhet", "unknown")
        persona_str = f"{roll}/{erfarenhet}"
    else:
        persona_str = str(persona_dict) if persona_dict else "unknown"

    # Extract validation score with graceful default
    validation = entry.get("validation", {})
    if isinstance(validation, dict):
        validation_score = validation.get("composite_score", 0.0)
    else:
        validation_score = 0.0

    return {
        "question": entry.get("question", ""),
        "answer": entry.get("answer", ""),
        "source": entry.get("source_document", ""),
        "persona": persona_str,
        "validation_score": validation_score,
    }


def transform_to_hf_rejected(entry: dict) -> dict:
    """
    Transform a rejected QA entry to HuggingFace format with failure reason.

    Same as transform_to_hf but includes failure_reason field.

    Args:
        entry: Dict with question, answer, persona, validation (with failure_reason)

    Returns:
        Flat dict with: question, answer, source, persona, validation_score, failure_reason
    """
    result = transform_to_hf(entry)

    # Add failure reason from validation
    validation = entry.get("validation", {})
    if isinstance(validation, dict):
        result["failure_reason"] = validation.get("failure_reason", "unknown")
    else:
        result["failure_reason"] = "unknown"

    return result


def read_jsonl_streaming(path: Path) -> Iterator[dict]:
    """
    Stream JSONL entries without loading entire file.

    Args:
        path: Path to JSONL file

    Yields:
        Parsed dict for each non-empty line
    """
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                yield json.loads(line)


def export_hf_jsonl(
    input_path: Path,
    output_path: Path,
    include_rejected: bool = False
) -> dict:
    """
    Export validated QA pairs to HuggingFace-compatible JSONL format.

    Reads from input JSONL (streaming), transforms each entry to flat format,
    and writes to output with ensure_ascii=False for Swedish characters.

    Args:
        input_path: Path to input JSONL (qa_passed.jsonl or qa_rejected.jsonl)
        output_path: Path for output HuggingFace-compatible JSONL
        include_rejected: If True, include failure_reason in output

    Returns:
        Stats dict: {"total": N, "exported": N}
    """
    total = 0
    exported = 0

    # Select transform function based on mode
    transform_fn = transform_to_hf_rejected if include_rejected else transform_to_hf

    with open(output_path, 'w', encoding='utf-8') as out_f:
        for entry in read_jsonl_streaming(input_path):
            total += 1
            try:
                hf_entry = transform_fn(entry)
                out_f.write(json.dumps(hf_entry, ensure_ascii=False) + '\n')
                exported += 1
            except Exception as e:
                # Skip entries that fail to transform (log but continue)
                continue

    return {"total": total, "exported": exported}

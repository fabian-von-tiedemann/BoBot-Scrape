# Phase 27: Core Infrastructure - Research

**Researched:** 2026-01-25
**Domain:** Pydantic models, YAML configuration, Python CLI scaffolding
**Confidence:** HIGH

## Summary

Phase 27 establishes the foundational infrastructure for the QA generation pipeline: a persona data model, YAML configuration loading, and CLI scaffold. The research confirms that the existing project stack (Pydantic 2.12.5, PyYAML 6.0.3) provides everything needed. No new dependencies are required except optionally Rich for progress bars.

The standard approach is to use Pydantic BaseModel for the Persona class with Literal types for constrained fields (proficiency levels), and a simple `yaml.safe_load()` + `model_validate()` pattern for configuration loading. The CLI scaffold should follow the existing project pattern (argparse with `--input`, `--output`, help epilog with examples).

**Primary recommendation:** Use existing dependencies (Pydantic 2, PyYAML) with minimal patterns; follow existing codebase conventions exactly for CLI and module structure.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pydantic | 2.12.5 | Data models with validation | Already installed, used in src/ai/gemini.py |
| pyyaml | 6.0.3 | YAML parsing | Already installed, standard for config |
| argparse | stdlib | CLI argument parsing | Standard lib, used throughout project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| rich | 14.x | Progress bars, console output | Optional: for `track()` progress during processing |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pyyaml | ruamel.yaml | Preserves comments/formatting but unnecessary for this use case |
| argparse | click/typer | More decorators but adds dependency; argparse matches existing code |
| pydantic BaseModel | dataclass | Loses validation; use Pydantic for consistency with gemini.py |

**Installation:**
```bash
# Core dependencies already installed
pip install rich  # Optional, for progress bars
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── qa/                      # New module for QA generation
│   ├── __init__.py          # Exports Persona, load_personas
│   ├── persona.py           # Persona model and loading
│   ├── questions.py         # Phase 28: Question generation (placeholder)
│   ├── answers.py           # Phase 29: Answer generation (placeholder)
│   ├── validation.py        # Phase 30: Validation (placeholder)
│   └── export.py            # Phase 31: Export (placeholder)
config/
└── personas.yaml            # Persona configuration file
generate_qa.py               # CLI script at project root (matches pipeline.py pattern)
```

### Pattern 1: Pydantic Model with Literal Types
**What:** Use Literal for constrained string fields to get validation at parse time
**When to use:** When field has a known, fixed set of valid values
**Example:**
```python
# Source: https://docs.pydantic.dev/latest/concepts/fields/
from typing import Literal
from pydantic import BaseModel, Field, computed_field

class Persona(BaseModel):
    """A care worker persona for QA generation."""
    roll: Literal["underskoterska"] = Field(
        description="Yrkesroll - endast underskoterska i v1"
    )
    erfarenhet: Literal["nyanstald", "erfaren"] = Field(
        description="Erfarenhetsniva"
    )
    situation: str = Field(
        description="Arbetssituation (t.ex. 'jobbar natt', 'vikarie')"
    )
    sprakbakgrund: Literal["native", "fluent", "intermediate", "beginner"] = Field(
        description="Svenskkunskaper"
    )

    @computed_field
    @property
    def id(self) -> str:
        """Auto-generate ID from fields: roll-erfarenhet-sprakbakgrund"""
        return f"{self.roll}-{self.erfarenhet}-{self.sprakbakgrund}"
```

### Pattern 2: YAML Loading with Validation
**What:** Load YAML and validate through Pydantic in one step
**When to use:** Loading configuration files
**Example:**
```python
# Source: https://techoverflow.net/2024/09/25/pydantic-how-to-load-store-model-in-yaml-file-minimal-example/
import yaml
from pathlib import Path
from pydantic import BaseModel

class PersonaConfig(BaseModel):
    """Container for persona configuration."""
    personas: list[Persona]

def load_personas(config_path: Path) -> list[Persona]:
    """Load and validate personas from YAML config."""
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    config = PersonaConfig.model_validate(data)
    return config.personas
```

### Pattern 3: CLI Script Following Project Convention
**What:** argparse with --input, --output, consistent with pipeline.py and generate_prompts.py
**When to use:** Any new CLI script in this project
**Example:**
```python
# Source: existing project pattern from generate_prompts.py
#!/usr/bin/env python3
"""
QA Generation Pipeline: Generate Q&A pairs from converted documents.

Usage:
    python generate_qa.py --input converted/ --output qa/
"""
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs from converted documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Generate with default settings
  %(prog)s --input converted/       Custom input directory
  %(prog)s --personas config/p.yaml Custom persona config
        """
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=Path("converted/"),
        help="Input directory with markdown documents (default: converted/)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("qa/"),
        help="Output directory for Q&A files (default: qa/)"
    )
    parser.add_argument(
        "--personas",
        type=Path,
        default=Path("config/personas.yaml"),
        help="Persona configuration file (default: config/personas.yaml)"
    )
    return parser.parse_args()
```

### Pattern 4: Module __init__.py Exports
**What:** Export key classes/functions from __init__.py for clean imports
**When to use:** Every new module
**Example:**
```python
# Source: existing pattern from src/ai/__init__.py
"""
QA generation module for BoBot-Scrape.

Provides persona-based Q&A generation for care worker training.
"""
from .persona import Persona, load_personas

__all__ = ['Persona', 'load_personas']
```

### Anti-Patterns to Avoid
- **Complex YAML with pydantic-settings:** Don't use YamlConfigSettingsSource for simple config loading; overkill for static config
- **Separate validation step:** Don't load YAML then manually validate fields; use `model_validate()` directly
- **Custom ID generation logic:** Don't create separate ID generator; use `@computed_field` on the model
- **Breaking existing patterns:** Don't introduce new CLI libraries (click/typer) when argparse is used everywhere

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Data validation | Manual type checking | Pydantic `model_validate()` | Handles edge cases, clear errors |
| YAML parsing | Custom parser | `yaml.safe_load()` | Battle-tested, secure |
| Progress display | Print statements | `rich.progress.track()` | Smooth updates, ETA, no flicker |
| Enum-like constraints | Custom validation | `Literal["a", "b"]` | Pydantic validates automatically |
| Auto-generated IDs | External function | `@computed_field` | Stays in sync with model |

**Key insight:** Pydantic 2 handles most validation complexity; use its features rather than reimplementing.

## Common Pitfalls

### Pitfall 1: Forgetting model_validate() for dict input
**What goes wrong:** Passing dict directly to model constructor works but misses some validation
**Why it happens:** Both `Model(**dict)` and `Model.model_validate(dict)` work
**How to avoid:** Always use `model_validate()` for external data (YAML, JSON)
**Warning signs:** Subtle validation errors only appearing in production

### Pitfall 2: Using unsafe YAML loading
**What goes wrong:** `yaml.load()` without Loader can execute arbitrary code
**Why it happens:** Old tutorials show `yaml.load(f)` without Loader parameter
**How to avoid:** Always use `yaml.safe_load()` for untrusted input
**Warning signs:** Security warnings in linters

### Pitfall 3: Inconsistent CLI patterns
**What goes wrong:** New script uses different argument names/patterns than existing scripts
**Why it happens:** Not checking existing codebase for conventions
**How to avoid:** Check pipeline.py, convert.py, generate_prompts.py for patterns
**Warning signs:** Inconsistent `--input` vs `-i` vs `--source` naming

### Pitfall 4: Not using Path objects consistently
**What goes wrong:** Mixing str and Path causes type errors or inconsistent path handling
**Why it happens:** argparse returns str by default
**How to avoid:** Use `type=Path` in argument parser
**Warning signs:** `str + str` path concatenation instead of `/`

### Pitfall 5: Exposing mutable default in Pydantic
**What goes wrong:** `field: list = []` shares list between instances
**Why it happens:** Python's mutable default argument trap
**How to avoid:** Use `Field(default_factory=list)`
**Warning signs:** Multiple instances sharing same list

## Code Examples

Verified patterns from official sources:

### Complete Persona Model
```python
# Source: Pydantic docs, project conventions
from typing import Literal
from pydantic import BaseModel, Field, computed_field

class Persona(BaseModel):
    """A care worker persona for generating realistic QA pairs.

    Personas represent different underskoterskor with varying experience
    and Swedish proficiency levels. Used to generate diverse, realistic
    questions that reflect actual workplace scenarios.
    """
    roll: Literal["underskoterska"] = Field(
        description="Yrkesroll"
    )
    erfarenhet: Literal["nyanstald", "erfaren"] = Field(
        description="Erfarenhetsniva i arbetsrollen"
    )
    situation: str = Field(
        description="Specifik arbetssituation (t.ex. 'jobbar natt i hemtjansten')"
    )
    sprakbakgrund: Literal["native", "fluent", "intermediate", "beginner"] = Field(
        description="Niva av svenskkunskaper"
    )

    @computed_field
    @property
    def id(self) -> str:
        """Generate readable ID from persona attributes."""
        return f"{self.roll}-{self.erfarenhet}-{self.sprakbakgrund}"
```

### YAML Configuration Format
```yaml
# config/personas.yaml
# Personas for QA generation - underskoterskor with varied backgrounds
personas:
  - roll: underskoterska
    erfarenhet: nyanstald
    situation: forsta manaden i hemtjansten
    sprakbakgrund: native

  - roll: underskoterska
    erfarenhet: erfaren
    situation: 10 ars erfarenhet, jobbar natt
    sprakbakgrund: native

  - roll: underskoterska
    erfarenhet: nyanstald
    situation: nyexaminerad, vikarie
    sprakbakgrund: intermediate

  - roll: underskoterska
    erfarenhet: erfaren
    situation: teamledare i hemtjansten
    sprakbakgrund: fluent

  - roll: underskoterska
    erfarenhet: nyanstald
    situation: karriarbytare, tidigare lagerarbetare
    sprakbakgrund: beginner
```

### Configuration Loading
```python
# Source: yaml.safe_load + Pydantic pattern
import yaml
from pathlib import Path
from pydantic import BaseModel

class PersonaConfig(BaseModel):
    """Root configuration containing list of personas."""
    personas: list[Persona]

def load_personas(config_path: Path) -> list[Persona]:
    """
    Load and validate personas from YAML configuration.

    Args:
        config_path: Path to personas.yaml file

    Returns:
        List of validated Persona instances

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If YAML doesn't match expected schema
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Persona config not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    config = PersonaConfig.model_validate(data)
    return config.personas
```

### CLI Scaffold with Progress
```python
# Source: rich docs, project conventions
#!/usr/bin/env python3
"""Generate Q&A pairs from converted documents."""
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs from converted documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Use defaults
  %(prog)s --input converted/           Custom input
  %(prog)s --file converted/doc.md      Single file mode
        """
    )
    parser.add_argument("--input", "-i", type=Path, default=Path("converted/"))
    parser.add_argument("--output", "-o", type=Path, default=Path("qa/"))
    parser.add_argument("--personas", type=Path, default=Path("config/personas.yaml"))
    parser.add_argument("--file", type=Path, help="Process single file (for testing)")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    # Validation
    if not args.input.exists():
        print(f"Error: Input directory {args.input} does not exist")
        return 1
    args.output.mkdir(parents=True, exist_ok=True)

    # TODO: Phase 28+ implementation
    print(f"Would process {args.input} -> {args.output}")
    return 0

if __name__ == "__main__":
    exit(main())
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Pydantic v1 validators | Pydantic v2 `model_validate()` | 2023 | Breaking API changes |
| `yaml.load(f)` | `yaml.safe_load(f)` | Always | Security requirement |
| dataclasses | Pydantic BaseModel | Current best practice | Better validation, JSON schema |
| print() progress | rich.progress.track() | 2020+ | Better UX for long operations |

**Deprecated/outdated:**
- `validator` decorator (Pydantic v1) - use `field_validator` in v2
- `__root__` for root models - use `RootModel` class in v2
- `Config` inner class - use `model_config = ConfigDict(...)` in v2

## Open Questions

Things that couldn't be fully resolved:

1. **Rich dependency decision**
   - What we know: Rich provides excellent progress bars, not currently installed
   - What's unclear: Whether to add dependency or use simple print statements
   - Recommendation: Optional - use Rich if user wants progress bars, fall back to print

2. **Experience level affecting question complexity**
   - What we know: CONTEXT.md marks this as Claude's discretion
   - What's unclear: Whether to implement in Phase 27 or defer to Phase 28
   - Recommendation: Add field to model but don't implement logic until Phase 28

## Sources

### Primary (HIGH confidence)
- [Pydantic Models Documentation](https://docs.pydantic.dev/latest/concepts/models/) - Model definition, validation, serialization
- [Pydantic Fields Documentation](https://docs.pydantic.dev/latest/concepts/fields/) - Field types, Literal, computed_field
- [Rich Progress Documentation](https://rich.readthedocs.io/en/latest/progress.html) - Progress bar patterns

### Secondary (MEDIUM confidence)
- [TechOverflow Pydantic YAML](https://techoverflow.net/2024/09/25/pydantic-how-to-load-store-model-in-yaml-file-minimal-example/) - Simple YAML loading pattern
- [Python argparse Documentation](https://docs.python.org/3/library/argparse.html) - CLI argument parsing
- Existing codebase: src/ai/gemini.py, generate_prompts.py, pipeline.py - Project conventions

### Tertiary (LOW confidence)
- None - all patterns verified with authoritative sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using already-installed, battle-tested libraries
- Architecture: HIGH - Following existing codebase patterns exactly
- Pitfalls: HIGH - Well-documented in official Pydantic docs

**Research date:** 2026-01-25
**Valid until:** 2026-03-25 (stable domain, Pydantic 2 mature)

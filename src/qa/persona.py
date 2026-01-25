"""
Persona model for QA generation.

Provides the Persona data model and configuration loading for generating
realistic Q&A pairs from care worker perspectives.
"""
from typing import Literal
from pathlib import Path

import yaml
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

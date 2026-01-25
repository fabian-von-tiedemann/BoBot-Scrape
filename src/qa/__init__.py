"""
QA generation module for BoBot-Scrape.

Provides persona-based Q&A generation for care worker training.
"""
from .persona import Persona, load_personas

__all__ = ['Persona', 'load_personas']

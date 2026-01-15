"""
AI module for BoBot-Scrape.

Provides AI-powered metadata generation using Gemini.
"""
from .gemini import generate_metadata, batch_generate_metadata, DocumentMetadata

__all__ = ['generate_metadata', 'batch_generate_metadata', 'DocumentMetadata']

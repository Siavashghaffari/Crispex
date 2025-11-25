"""
Crispex - AI-powered CRISPR sgRNA design

Main module providing the public API for guide design.
"""

from crispex.api import design_guides
from crispex.utils.errors import CrispexError, GeneNotFoundError, GenomeNotInstalledError

__version__ = "0.1.0"
__all__ = [
    "design_guides",
    "CrispexError",
    "GeneNotFoundError",
    "GenomeNotInstalledError",
]

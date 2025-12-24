"""
Shared library for MCP scripts.

These are extracted and simplified from repo code to minimize dependencies.
"""

from .io import *
from .utils import *

__all__ = ['load_json', 'save_json', 'read_fasta', 'validate_sequence', 'clean_filename']
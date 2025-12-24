"""Shared I/O functions for MCP scripts.

These are extracted and simplified from repo code to minimize dependencies.
"""
from pathlib import Path
from typing import Union, Any, List, Tuple
import json
import re


def load_json(file_path: Union[str, Path]) -> dict:
    """Load JSON file."""
    with open(file_path) as f:
        return json.load(f)


def save_json(data: dict, file_path: Union[str, Path]) -> None:
    """Save data to JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def read_fasta(file_path: Union[str, Path]) -> List[Tuple[str, str]]:
    """
    Read FASTA file and return list of (header, sequence) tuples.
    Simplified from esm.data.read_fasta for independence.

    Args:
        file_path: Path to FASTA file

    Returns:
        List of (header, sequence) tuples
    """
    sequences = []
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"FASTA file not found: {file_path}")

    with open(file_path, 'r') as f:
        header = None
        sequence_lines = []

        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence if exists
                if header is not None:
                    sequence = ''.join(sequence_lines)
                    if sequence:  # Only add non-empty sequences
                        sequences.append((header, sequence))

                # Start new sequence
                header = line[1:]  # Remove '>'
                sequence_lines = []
            elif header is not None:
                # Add sequence line (remove any whitespace)
                clean_line = ''.join(line.split())
                if clean_line:
                    sequence_lines.append(clean_line)

        # Add last sequence
        if header is not None:
            sequence = ''.join(sequence_lines)
            if sequence:
                sequences.append((header, sequence))

    if not sequences:
        raise ValueError(f"No valid sequences found in FASTA file: {file_path}")

    return sequences


def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Clean filename safe for filesystem
    """
    # Remove or replace invalid characters
    clean = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing whitespace and dots
    clean = clean.strip(' .')
    # Limit length
    if len(clean) > 255:
        clean = clean[:255]
    # Ensure not empty
    if not clean:
        clean = "unnamed"
    return clean
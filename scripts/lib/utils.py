"""General utility functions for MCP scripts.

These are extracted and simplified from repo code to minimize dependencies.
"""
import re
from typing import Optional, List


# Valid amino acid characters
VALID_AA_CHARS = set('ACDEFGHIKLMNPQRSTVWY')
VALID_AA_EXTENDED = VALID_AA_CHARS | set('BJOUXZ')  # Include rare/ambiguous AAs


def validate_sequence(sequence: str, strict: bool = True) -> bool:
    """
    Validate protein sequence.

    Args:
        sequence: Protein sequence string
        strict: If True, only allow standard 20 amino acids

    Returns:
        True if valid, False otherwise
    """
    if not sequence:
        return False

    # Remove whitespace
    clean_seq = ''.join(sequence.split()).upper()

    # Check characters
    valid_chars = VALID_AA_CHARS if strict else VALID_AA_EXTENDED
    return all(c in valid_chars for c in clean_seq)


def clean_sequence(sequence: str, strict: bool = True) -> str:
    """
    Clean protein sequence by removing invalid characters.

    Args:
        sequence: Raw protein sequence
        strict: If True, only allow standard 20 amino acids

    Returns:
        Cleaned sequence
    """
    if not sequence:
        return ""

    # Remove whitespace and convert to uppercase
    clean_seq = ''.join(sequence.split()).upper()

    # Filter valid characters
    valid_chars = VALID_AA_CHARS if strict else VALID_AA_EXTENDED
    clean_seq = ''.join(c for c in clean_seq if c in valid_chars)

    return clean_seq


def parse_sequence_header(header: str) -> dict:
    """
    Parse FASTA sequence header to extract metadata.

    Args:
        header: FASTA header line (without '>')

    Returns:
        Dict with parsed metadata
    """
    metadata = {'raw_header': header}

    # Try to extract common patterns
    # UniProt format: sp|P12345|GENE_HUMAN Description
    uniprot_match = re.match(r'([a-z]{2})\|([A-Z0-9]+)\|([A-Z0-9_]+)\s*(.*)', header)
    if uniprot_match:
        metadata.update({
            'database': uniprot_match.group(1),
            'accession': uniprot_match.group(2),
            'entry_name': uniprot_match.group(3),
            'description': uniprot_match.group(4).strip()
        })
        return metadata

    # Simple format: ID Description
    parts = header.split(None, 1)
    metadata['id'] = parts[0] if parts else header
    metadata['description'] = parts[1] if len(parts) > 1 else ""

    return metadata


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """
    Split list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Maximum size of each chunk

    Returns:
        List of chunks
    """
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunks.append(items[i:i + chunk_size])
    return chunks


def estimate_memory_usage(sequence_length: int, model_size: str = "650M") -> float:
    """
    Estimate memory usage for ESM model inference.

    Args:
        sequence_length: Length of protein sequence
        model_size: Model size string (e.g., "650M", "3B")

    Returns:
        Estimated memory usage in GB
    """
    # Base model memory usage (approximate)
    model_memory = {
        "8M": 0.1,
        "35M": 0.2,
        "150M": 0.5,
        "650M": 2.5,
        "3B": 12.0,
        "15B": 60.0
    }

    # Extract size from model name
    base_mem = model_memory.get(model_size, 2.5)

    # Sequence-dependent memory (rough estimation)
    # Attention is O(L^2), embeddings are O(L)
    seq_mem = (sequence_length ** 2) * 4e-9  # 4 bytes per float, rough scaling

    return base_mem + seq_mem
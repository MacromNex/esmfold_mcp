#!/usr/bin/env python3
"""
Script: protein_embeddings.py
Description: Extract protein sequence embeddings using ESM-2 language model

Original Use Case: examples/use_case_3_protein_embeddings.py
Dependencies Removed: Simplified setup_environment function, inlined FASTA reading

Usage:
    python scripts/protein_embeddings.py --input <input_file> --output <output_dir>

Example:
    python scripts/protein_embeddings.py --input examples/data/few_proteins.fasta --output results/embeddings/
    python scripts/protein_embeddings.py --sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" --output results/single/
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
import json

# Essential scientific packages
import numpy as np
import torch

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "model_name": "esm2_t33_650M_UR50D",
    "repr_layers": [33],
    "include_mean": True,
    "include_per_tok": False,
    "include_bos": False,
    "include_contacts": False,
    "device": "auto",
    "output_format": "npz",
    "batch_size": 1  # Keep simple for MCP
}

# Available ESM-2 models
AVAILABLE_MODELS = [
    "esm2_t6_8M_UR50D",
    "esm2_t12_35M_UR50D",
    "esm2_t30_150M_UR50D",
    "esm2_t33_650M_UR50D",
    "esm2_t36_3B_UR50D",
    "esm2_t48_15B_UR50D"
]

# ==============================================================================
# Inlined Utility Functions (simplified from repo)
# ==============================================================================
def read_fasta(file_path: Union[str, Path]) -> List[Tuple[str, str]]:
    """
    Read FASTA file and return list of (header, sequence) tuples.
    Inlined from esm.data.read_fasta for independence.

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


def load_esm_model(model_name: str = "esm2_t33_650M_UR50D"):
    """
    Lazy load ESM model with error handling.

    Args:
        model_name: ESM model name to load

    Returns:
        Tuple of (model, alphabet, batch_converter)
    """
    try:
        import esm
        print(f"✓ ESM package loaded successfully")
    except ImportError as e:
        print(f"✗ Error importing ESM: {e}")
        print("Please ensure fair-esm package is installed:")
        print("  pip install fair-esm")
        raise

    try:
        print(f"Loading ESM-2 model: {model_name}")
        model, alphabet = getattr(esm.pretrained, model_name)()
        batch_converter = alphabet.get_batch_converter()
        model.eval()
        return model, alphabet, batch_converter
    except AttributeError:
        print(f"✗ Unknown model: {model_name}")
        print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
        raise
    except Exception as e:
        print(f"✗ Error loading model {model_name}: {e}")
        raise


def save_embeddings_npz(embeddings: Dict[str, Any], output_dir: Path) -> List[Path]:
    """Save embeddings in NPZ format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    for label, data in embeddings.items():
        # Clean filename
        safe_label = "".join(c for c in label if c.isalnum() or c in "._-")
        output_file = output_dir / f"{safe_label}.npz"

        # Prepare data for saving
        save_data = {}
        for k, v in data.items():
            if isinstance(v, np.ndarray):
                save_data[k] = v
            elif k == 'sequence':
                save_data['sequence'] = np.array(str(v), dtype='U1')
            elif k in ['length', 'label']:
                save_data[k] = np.array(v)

        np.savez_compressed(output_file, **save_data)
        output_files.append(output_file)
        print(f"Saved embeddings for '{label}' to {output_file}")

    return output_files


def save_embeddings_json(embeddings: Dict[str, Any], output_dir: Path) -> List[Path]:
    """Save embeddings metadata and mean embeddings in JSON format (for inspection)."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = []

    for label, data in embeddings.items():
        # Clean filename
        safe_label = "".join(c for c in label if c.isalnum() or c in "._-")
        output_file = output_dir / f"{safe_label}.json"

        # Prepare JSON-serializable data (metadata + mean embeddings)
        json_data = {
            'label': data['label'],
            'sequence': data['sequence'],
            'length': data['length']
        }

        # Add mean embeddings if available
        for k, v in data.items():
            if k.startswith('mean_layer_') and isinstance(v, np.ndarray):
                json_data[k] = {
                    'shape': list(v.shape),
                    'norm': float(np.linalg.norm(v)),
                    'mean': float(np.mean(v)),
                    'std': float(np.std(v)),
                    'values': v.tolist()  # Full embedding
                }

        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)

        output_files.append(output_file)
        print(f"Saved embedding metadata for '{label}' to {output_file}")

    return output_files

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_protein_embeddings(
    input_file: Optional[Union[str, Path]] = None,
    sequence: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Extract protein sequence embeddings using ESM-2.

    Args:
        input_file: Path to FASTA file (mutually exclusive with sequence)
        sequence: Single protein sequence string (mutually exclusive with input_file)
        output_dir: Directory to save embeddings (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - embeddings: Dict of embeddings by sequence label
            - output_files: List of output file paths (if saved)
            - metadata: Execution metadata

    Example:
        >>> result = run_protein_embeddings(input_file="input.fasta", output_dir="embeddings/")
        >>> print(result['output_files'])

        >>> result = run_protein_embeddings(sequence="MKTVR...", output_dir="single/")
        >>> print(result['embeddings']['single_sequence']['mean_layer_33'].shape)
    """
    # Setup configuration
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Validate inputs
    if input_file and sequence:
        raise ValueError("Specify either input_file or sequence, not both")
    if not input_file and not sequence:
        raise ValueError("Must specify either input_file or sequence")

    # Prepare sequences
    if sequence:
        sequences = [("single_sequence", sequence)]
    else:
        input_file = Path(input_file)
        sequences = read_fasta(input_file)
        print(f"Loaded {len(sequences)} sequences from {input_file}")

    # Load ESM model
    model, alphabet, batch_converter = load_esm_model(config['model_name'])

    # Setup device
    device = config['device']
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if device == "cuda" and torch.cuda.is_available():
        model = model.cuda()
        print("Using GPU")
    else:
        model = model.cpu()
        print("Using CPU")

    # Extract embeddings
    print(f"Extracting representations from layer(s): {config['repr_layers']}")

    # Convert sequences to model input format
    batch_labels, batch_strs, batch_tokens = batch_converter(sequences)
    if device == "cuda":
        batch_tokens = batch_tokens.cuda()

    batch_lens = (batch_tokens != alphabet.padding_idx).sum(1)

    results = {}

    with torch.no_grad():
        model_output = model(
            batch_tokens,
            repr_layers=config['repr_layers'],
            return_contacts=config['include_contacts']
        )

        for i, (label, seq, tokens_len) in enumerate(zip(batch_labels, batch_strs, batch_lens)):
            print(f"Processing sequence {i+1}/{len(sequences)}: {label}")

            result = {
                'label': label,
                'sequence': seq,
                'length': len(seq)
            }

            # Extract representations from each layer
            for layer in config['repr_layers']:
                layer_repr = model_output["representations"][layer][i]

                if config['include_mean']:
                    # Mean-pool over sequence (excluding special tokens)
                    sequence_repr = layer_repr[1:tokens_len-1].mean(0)
                    result[f'mean_layer_{layer}'] = sequence_repr.cpu().numpy()

                if config['include_per_tok']:
                    # Per-token representations (excluding special tokens)
                    token_repr = layer_repr[1:tokens_len-1]
                    result[f'per_tok_layer_{layer}'] = token_repr.cpu().numpy()

                if config['include_bos']:
                    # Beginning-of-sequence representation
                    bos_repr = layer_repr[0]
                    result[f'bos_layer_{layer}'] = bos_repr.cpu().numpy()

            # Attention contacts
            if config['include_contacts']:
                attention_contacts = model_output["contacts"][i]
                result['attention_contacts'] = attention_contacts[:tokens_len, :tokens_len].cpu().numpy()

            results[label] = result

    # Save embeddings if output directory specified
    output_files = []
    if output_dir:
        output_dir = Path(output_dir)

        if config['output_format'] == 'npz':
            output_files.extend(save_embeddings_npz(results, output_dir))
        elif config['output_format'] == 'json':
            output_files.extend(save_embeddings_json(results, output_dir))
        elif config['output_format'] == 'both':
            output_files.extend(save_embeddings_npz(results, output_dir))
            output_files.extend(save_embeddings_json(results, output_dir / "metadata"))

    return {
        "embeddings": results,
        "output_files": [str(f) for f in output_files] if output_files else None,
        "metadata": {
            "input_file": str(input_file) if input_file else None,
            "sequence_count": len(sequences),
            "config": config,
            "device_used": device
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", "-i", help="Input FASTA file path")
    input_group.add_argument("--sequence", "-s", help="Single protein sequence")

    # Output options
    parser.add_argument("--output", "-o", help="Output directory path")
    parser.add_argument("--config", "-c", help="Config file (JSON)")

    # Model options
    parser.add_argument("--model", choices=AVAILABLE_MODELS,
                       default=DEFAULT_CONFIG["model_name"],
                       help=f"ESM-2 model to use (default: {DEFAULT_CONFIG['model_name']})")
    parser.add_argument("--repr-layers", nargs='+', type=int,
                       default=DEFAULT_CONFIG["repr_layers"],
                       help=f"Representation layers to extract (default: {DEFAULT_CONFIG['repr_layers']})")

    # Representation options
    parser.add_argument("--include-per-tok", action="store_true",
                       help="Include per-token (per-residue) representations")
    parser.add_argument("--include-bos", action="store_true",
                       help="Include beginning-of-sequence token representation")
    parser.add_argument("--include-contacts", action="store_true",
                       help="Include attention-based contact predictions")

    # Device options
    parser.add_argument("--device", choices=['auto', 'cuda', 'cpu'],
                       default=DEFAULT_CONFIG["device"],
                       help="Device to use for computation")

    # Output format
    parser.add_argument("--format", choices=['npz', 'json', 'both'],
                       default=DEFAULT_CONFIG["output_format"],
                       help="Output format")

    args = parser.parse_args()

    try:
        # Load config if provided
        config = None
        if args.config:
            with open(args.config) as f:
                config = json.load(f)

        # Override config with command line arguments
        config_overrides = {
            "model_name": args.model,
            "repr_layers": args.repr_layers,
            "include_per_tok": args.include_per_tok,
            "include_bos": args.include_bos,
            "include_contacts": args.include_contacts,
            "device": args.device,
            "output_format": args.format
        }

        # Run extraction
        result = run_protein_embeddings(
            input_file=args.input,
            sequence=args.sequence,
            output_dir=args.output,
            config=config,
            **config_overrides
        )

        # Print summary
        print(f"\n✓ Embedding extraction completed successfully!")
        if result['output_files']:
            print(f"Results saved to: {len(result['output_files'])} files")
            for f in result['output_files'][:3]:  # Show first 3 files
                print(f"  - {f}")
            if len(result['output_files']) > 3:
                print(f"  ... and {len(result['output_files']) - 3} more")

        # Print embedding summary
        embeddings = result['embeddings']
        print(f"\nExtracted embeddings for {len(embeddings)} sequence(s):")
        for label, data in embeddings.items():
            print(f"  - {label}: {data['length']} residues")
            for key in data:
                if key.startswith('mean_layer_'):
                    layer = key.split('_')[-1]
                    shape = data[key].shape
                    print(f"    └─ Layer {layer} mean embedding: {shape}")

        return result

    except KeyboardInterrupt:
        print("\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
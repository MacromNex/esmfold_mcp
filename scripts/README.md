# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported
2. **Self-Contained**: Functions inlined where possible
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Repo Dependent | Config |
|--------|-------------|----------------|--------|
| `protein_embeddings.py` | Extract ESM-2 protein embeddings | Yes (fair-esm) | `configs/protein_embeddings_config.json` |

## Usage

```bash
# Activate environment (use the working ESM environment)
mamba activate ./env_esmfold  # or: conda activate ./env_esmfold

# Extract embeddings from FASTA file
python scripts/protein_embeddings.py --input examples/data/few_proteins.fasta --output results/embeddings/

# Extract embeddings from single sequence
python scripts/protein_embeddings.py --sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" --output results/single/

# Use different model and options
python scripts/protein_embeddings.py --input FILE --output DIR --model esm2_t6_8M_UR50D --include-per-tok

# With custom config
python scripts/protein_embeddings.py --input FILE --output DIR --config configs/custom.json
```

## Available Options

### protein_embeddings.py

**Input Options (mutually exclusive):**
- `--input`, `-i`: Path to FASTA file
- `--sequence`, `-s`: Single protein sequence string

**Output Options:**
- `--output`, `-o`: Output directory path
- `--format`: Output format (`npz`, `json`, `both`)

**Model Options:**
- `--model`: ESM-2 model to use:
  - `esm2_t6_8M_UR50D` (fastest, 8M parameters)
  - `esm2_t12_35M_UR50D` (35M parameters)
  - `esm2_t30_150M_UR50D` (150M parameters)
  - `esm2_t33_650M_UR50D` (default, 650M parameters)
  - `esm2_t36_3B_UR50D` (large, 3B parameters)
  - `esm2_t48_15B_UR50D` (largest, 15B parameters)
- `--repr-layers`: Which layers to extract (default: [33])

**Representation Options:**
- `--include-per-tok`: Include per-residue representations
- `--include-bos`: Include beginning-of-sequence token
- `--include-contacts`: Include attention-based contact predictions

**Computation Options:**
- `--device`: Device to use (`auto`, `cuda`, `cpu`)

**Configuration:**
- `--config`, `-c`: JSON config file path

## Shared Library

Common functions are in `scripts/lib/`:
- `io.py`: File loading/saving, FASTA reading
- `utils.py`: Sequence validation, memory estimation

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped:
```python
from scripts.protein_embeddings import run_protein_embeddings

# In MCP tool:
@mcp.tool()
def extract_protein_embeddings(
    input_file: str = None,
    sequence: str = None,
    output_dir: str = None
):
    return run_protein_embeddings(
        input_file=input_file,
        sequence=sequence,
        output_dir=output_dir
    )
```

## Dependencies

### protein_embeddings.py
- **Essential**: argparse, sys, pathlib, typing, json, numpy, torch
- **ESM Package**: fair-esm (installed from repo/esm)
- **Environment**: env_esmfold (Python 3.7.12, PyTorch 1.12.1+cpu)

**Note**: This script requires the fair-esm package which is installed from the local repo. It is not fully independent but has minimized dependencies within the ESM ecosystem.

## Testing

The scripts have been tested with the example data:
- ✅ `protein_embeddings.py` works with `examples/data/few_proteins.fasta`
- ✅ Single sequence input works
- ✅ Multiple output formats (npz, json, both)
- ✅ Different model sizes work
- ✅ GPU/CPU detection works

## Environment Requirements

Use the `env_esmfold` environment which has:
- Python 3.7.12
- PyTorch 1.12.1+cpu
- fair-esm 2.0.1 (from source)
- NumPy, einops (0.6.1), and other dependencies

To test:
```bash
mamba run -p ./env_esmfold python scripts/protein_embeddings.py --sequence "ACDEFGHIK" --output test/
```
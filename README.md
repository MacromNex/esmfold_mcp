# ESMfold MCP

> **Protein sequence analysis using ESM-2 language models via Model Context Protocol (MCP)**

This MCP server provides access to Meta's ESM-2 protein language models for extracting protein sequence embeddings and representations. It enables AI applications to analyze protein sequences using state-of-the-art protein language models.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Docker](#docker)

## Overview

The ESMfold MCP server provides protein sequence analysis capabilities through Meta's ESM-2 (Evolutionary Scale Modeling) family of protein language models. These models can extract rich sequence embeddings that capture evolutionary, structural, and functional information from protein sequences.

### Features
- **ESM-2 Protein Embeddings**: Extract representations from 6 different model sizes (8M to 15B parameters)
- **Batch Processing**: Handle multiple sequences and files efficiently
- **Flexible Output**: Support for NPZ, JSON, and combined formats
- **Job Management**: Background processing for large-scale analyses
- **Multiple Input Types**: Single sequences, FASTA files, and batch operations

### Directory Structure
```
./
├── README.md               # This file
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
├── quick_setup.sh          # Automated setup script
├── .github/workflows/      # CI/CD (Docker build & push)
├── env/                    # Main MCP environment (Python 3.10)
├── env_esmfold/            # ESM processing environment (Python 3.7)
├── src/
│   ├── server.py           # MCP server
│   └── jobs/               # Job manager for async operations
├── scripts/
│   ├── protein_embeddings.py  # ESM-2 embeddings extraction
│   └── lib/                # Shared utilities
├── examples/
│   └── data/               # Demo data
├── configs/                # Configuration files
├── jobs/                   # Job execution directory
└── repo/                   # Original ESM repository
```

---

## Installation

### Option 1: Docker (Recommended)

The easiest way to get started. A pre-built image is published to GHCR on every push to `main`.

```bash
# Pull the latest image
docker pull ghcr.io/macromnex/esmfold_mcp:latest

# Run the MCP server
docker run --gpus all ghcr.io/macromnex/esmfold_mcp:latest

# Or build locally
docker build -t esmfold_mcp .
docker run --gpus all esmfold_mcp
```

Register in Claude Code:
```bash
claude mcp add esmfold -- docker run --gpus all -i --rm ghcr.io/macromnex/esmfold_mcp:latest
```

To mount local data directories for input/output:
```bash
docker run --gpus all -i --rm \
  -v /path/to/your/fasta/files:/app/inputs \
  -v /path/to/save/results:/app/results \
  ghcr.io/macromnex/esmfold_mcp:latest
```

Register in Claude Code with mounted volumes:
```bash
claude mcp add esmfold -- docker run --gpus all -i --rm \
  -v /path/to/your/data:/app/inputs \
  -v /path/to/save/results:/app/results \
  ghcr.io/macromnex/esmfold_mcp:latest
```

### Option 2: Quick Setup (Conda)

Run the automated setup script:

```bash
cd esmfold_mcp
bash quick_setup.sh
```

The script will create both the main MCP environment and the ESMFold environment, install all dependencies, clone the ESM repository, and display the Claude Code configuration. See `quick_setup.sh --help` for options like `--skip-env` or `--skip-repo`.

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+ for MCP server and Python 3.7+ for ESM models
- NVIDIA GPU with CUDA support (optional, CPU fallback available)
- At least 8GB RAM (16GB+ recommended for larger models)

### Option 3: Manual Installation

If you prefer manual installation or need to customize the setup, follow the information in `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/esmfold_mcp

# Create main MCP environment with Python 3.10
mamba create -p ./env python=3.10 pip -y
# or: conda create -p ./env python=3.10 pip -y

# Activate main environment
mamba activate ./env
# or: conda activate ./env

# Install MCP dependencies
mamba run -p ./env pip install fastmcp loguru

# Create ESM environment with Python 3.7 from environment.yml
mamba env create -f repo/esm/environment.yml -p ./env_esmfold
# or: conda env create -f repo/esm/environment.yml -p ./env_esmfold

# Install ESM package in the ESM environment
mamba run -p ./env_esmfold pip install -e repo/esm/
```

### Verification

```bash
# Test main MCP environment
mamba run -p ./env python -c "import fastmcp; print('FastMCP ready')"

# Test ESM environment
mamba run -p ./env_esmfold python -c "import esm; print('ESM ready')"

# Test script
mamba run -p ./env_esmfold python scripts/protein_embeddings.py --help
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/protein_embeddings.py` | Extract ESM-2 protein embeddings | See below |

### Script Examples

#### Protein Embeddings Extraction

```bash
# Activate ESM environment
mamba activate ./env_esmfold

# Extract embeddings from FASTA file
python scripts/protein_embeddings.py \
  --input examples/data/few_proteins.fasta \
  --output results/embeddings/ \
  --model esm2_t33_650M_UR50D

# Extract embeddings from single sequence
python scripts/protein_embeddings.py \
  --sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" \
  --output results/single/ \
  --include-per-tok

# Use smallest model for fast testing
python scripts/protein_embeddings.py \
  --input examples/data/few_proteins.fasta \
  --output results/fast/ \
  --model esm2_t6_8M_UR50D \
  --format both

# With configuration file
python scripts/protein_embeddings.py \
  --input examples/data/some_proteins.fasta \
  --output results/configured/ \
  --config configs/protein_embeddings_config.json
```

**Parameters:**
- `--input, -i`: FASTA file with protein sequences (optional)
- `--sequence, -s`: Single protein sequence string (optional, mutually exclusive with input)
- `--output, -o`: Output directory path (optional, uses temp if not provided)
- `--model`: ESM-2 model (esm2_t6_8M_UR50D to esm2_t48_15B_UR50D, default: esm2_t33_650M_UR50D)
- `--repr-layers`: Layer numbers to extract (default: [33])
- `--include-per-tok`: Include per-residue representations
- `--include-bos`: Include beginning-of-sequence token
- `--include-contacts`: Include attention-based contact predictions
- `--device`: Computation device (auto, cuda, cpu)
- `--format`: Output format (npz, json, both)
- `--config`: JSON config file path

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name esmfold
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add esmfold -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "esmfold": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/esmfold_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/esmfold_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from esmfold?
```

#### Basic Usage
```
Use extract_protein_embeddings with input_file @examples/data/few_proteins.fasta
```

#### With Configuration
```
Extract protein embeddings from @examples/data/some_proteins.fasta using model esm2_t6_8M_UR50D and save to results/fast/
```

#### Long-Running Tasks (Submit API)
```
Submit protein embeddings extraction for @examples/data/P62593.fasta with model esm2_t48_15B_UR50D
Then check the job status
```

#### Batch Processing
```
Process these files in batch:
- @examples/data/few_proteins.fasta
- @examples/data/some_proteins.fasta
- @examples/data/P62593.fasta
Save results to results/batch/
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/few_proteins.fasta` | Reference a specific FASTA file |
| `@configs/protein_embeddings_config.json` | Reference a config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "esmfold": {
      "command": "/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/esmfold_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/ProteinMCP/ProteinMCP/tool-mcps/esmfold_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Use extract_protein_embeddings with file examples/data/few_proteins.fasta
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `extract_protein_embeddings` | Extract ESM-2 protein embeddings | `input_file`, `sequence`, `output_dir`, `model`, ... |
| `get_server_info` | Get server information and available models | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_protein_embeddings` | Submit protein embeddings extraction | `input_file`, `sequence`, `job_name`, ... |
| `submit_batch_protein_embeddings` | Submit batch processing for multiple files | `input_files`, `output_dir`, `batch_name`, ... |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs |

---

## Examples

### Example 1: Quick Protein Analysis

**Goal:** Extract embeddings from a small set of proteins

**Using Script:**
```bash
python scripts/protein_embeddings.py \
  --input examples/data/few_proteins.fasta \
  --output results/example1/
```

**Using MCP (in Claude Code):**
```
Use extract_protein_embeddings to process @examples/data/few_proteins.fasta and save results to results/example1/
```

**Expected Output:**
- NPZ files with sequence embeddings (1280-dimensional vectors)
- JSON metadata with sequence information

### Example 2: Large-Scale Analysis

**Goal:** Process a large protein dataset with the best model

**Using Script:**
```bash
python scripts/protein_embeddings.py \
  --input examples/data/P62593.fasta \
  --model esm2_t48_15B_UR50D \
  --output results/example2/
```

**Using MCP (in Claude Code):**
```
Submit protein embeddings extraction for @examples/data/P62593.fasta with model esm2_t48_15B_UR50D and save to results/example2/
```

### Example 3: Batch Processing

**Goal:** Process multiple files at once

**Using Script:**
```bash
for f in examples/data/*.fasta; do
  python scripts/protein_embeddings.py --input "$f" --output results/batch/
done
```

**Using MCP (in Claude Code):**
```
Submit batch processing for all FASTA files in @examples/data/ and save to results/batch/
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `few_proteins.fasta` | 3 short protein sequences for testing | Quick testing |
| `some_proteins.fasta` | ~20 protein sequences for batch testing | Batch processing |
| `P62593.fasta` | Large protein sequence collection | Large-scale analysis |
| `5YH2.pdb` | Reference protein structure | Structure analysis |
| `4uv3.pdb` | Multi-chain protein complex | Complex analysis |
| `5YH2_mutated_seqs.fasta` | Variant sequences for analysis | Mutation studies |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `protein_embeddings_config.json` | ESM-2 embeddings configuration | model, extraction, computation, output |

### Config Example

```json
{
  "model": {
    "name": "esm2_t33_650M_UR50D",
    "description": "ESM-2 650M parameter model (balance of performance and speed)"
  },
  "extraction": {
    "repr_layers": [33],
    "include_mean": true,
    "include_per_tok": false,
    "include_contacts": false
  },
  "computation": {
    "device": "auto",
    "batch_size": 1
  },
  "output": {
    "format": "npz",
    "save_metadata": true
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environments
mamba create -p ./env python=3.10 pip -y
mamba env create -f repo/esm/environment.yml -p ./env_esmfold
mamba run -p ./env pip install fastmcp loguru
mamba run -p ./env_esmfold pip install -e repo/esm/
```

**Problem:** Import errors
```bash
# Verify installations
mamba run -p ./env python -c "from src.server import mcp; print('MCP ready')"
mamba run -p ./env_esmfold python -c "import esm; print('ESM ready')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove esmfold
fastmcp install src/server.py --name esmfold
```

**Problem:** Tools not working
```bash
# Test server directly
mamba run -p ./env python -c "
from src.server import mcp
print('Available tools:', list(mcp.list_tools().keys()))
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
cat jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id "<job_id>" and tail 100 to see error details
```

### Model and Memory Issues

**Problem:** CUDA out of memory
```
Use device "cpu" parameter to force CPU processing
```

**Problem:** Model download fails
```bash
# Test model access
mamba run -p ./env_esmfold python -c "
import esm
model, alphabet = esm.pretrained.esm2_t6_8M_UR50D()
print('Model loaded successfully')
"
```

---

## Model Selection Guidelines

| Model | Parameters | Speed | Memory | Use Case |
|-------|------------|-------|--------|----------|
| esm2_t6_8M_UR50D | 8M | Fastest | ~1GB | Quick testing, many sequences |
| esm2_t12_35M_UR50D | 35M | Fast | ~2GB | Moderate analysis |
| esm2_t30_150M_UR50D | 150M | Medium | ~4GB | Good balance |
| esm2_t33_650M_UR50D | 650M | Medium | ~8GB | General use (default) |
| esm2_t36_3B_UR50D | 3B | Slow | ~16GB | High quality |
| esm2_t48_15B_UR50D | 15B | Slowest | ~32GB | Best quality, research |

### When to Use Submit API
- Large FASTA files (>100 sequences)
- Large models (esm2_t36_3B_UR50D, esm2_t48_15B_UR50D)
- When you need to continue other work
- Batch processing multiple files

### Output Formats
- **NPZ**: Efficient binary format for numerical data
- **JSON**: Human-readable, larger file size
- **Both**: Maximum compatibility

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test basic functionality
python -m pytest tests/ -v
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py
```

---

## Docker

### Image Details

The Docker image is based on `pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime` and includes:
- Python 3.11 with PyTorch 2.4.0 + CUDA 11.8
- ESM (from github.com/facebookresearch/esm)
- fastmcp 3.0
- All required dependencies

### Building Locally

```bash
docker build -t esmfold_mcp .
```

### CI/CD

A GitHub Actions workflow (`.github/workflows/docker.yml`) automatically builds and pushes the image to GHCR on:
- Every push to `main`
- Semantic version tags (`v*.*.*`)
- Manual workflow dispatch

Image tags:
- `latest` — latest build from `main`
- `sha-<commit>` — pinned to a specific commit
- `x.y.z` — semantic version (when tagged)

---

## License

Based on Meta's ESM repository. Please refer to the original repository for licensing terms.

## Credits

Based on [Meta AI ESM](https://github.com/facebookresearch/esm) - Evolutionary Scale Modeling for protein language modeling.
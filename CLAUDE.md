# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ESMfold MCP is a Model Context Protocol server that exposes Meta's ESM-2 protein language models for extracting protein sequence embeddings. It wraps the ESM-2 models (8M to 15B parameters) as MCP tools consumable by AI coding assistants like Claude Code and Gemini CLI.

## Architecture

**Dual-environment design:** The project uses two separate Python environments due to ESM's dependency constraints:
- `env/` — Python 3.10, runs the MCP server (fastmcp, loguru)
- `env_esmfold/` — Python 3.7, runs ESM model inference (PyTorch, esm)

**Key components:**
- `src/server.py` — FastMCP server entry point. Defines all MCP tools: sync tools (`extract_protein_embeddings`, `get_server_info`), async submit tools (`submit_protein_embeddings`, `submit_batch_protein_embeddings`), and job management tools (`get_job_status`, `get_job_result`, `get_job_log`, `cancel_job`, `list_jobs`).
- `src/jobs/manager.py` — `JobManager` class that handles background job execution via subprocess + threading. Jobs are stored as directories under `jobs/` with metadata JSON and log files.
- `scripts/protein_embeddings.py` — Standalone ESM-2 embedding extraction script. Has its own `run_protein_embeddings()` function that `server.py` imports for sync operations. Handles FASTA parsing, model loading, embedding extraction, and output in NPZ/JSON formats.
- `scripts/lib/` — Shared utilities (`io.py`, `utils.py`)
- `repo/esm/` — Cloned Facebook ESM repository (installed as editable package in `env_esmfold`)

**Sync vs Async pattern:** Sync tools import and call `run_protein_embeddings()` directly. Async submit tools construct CLI arguments and spawn the script as a subprocess via `JobManager`, which runs it in `env_esmfold` using `mamba run`.

## Build & Run Commands

```bash
# Setup environments (automated)
bash quick_setup.sh

# Run MCP server
mamba run -p ./env python src/server.py

# Run MCP server in dev mode
fastmcp dev src/server.py

# Run embedding extraction directly
mamba run -p ./env_esmfold python scripts/protein_embeddings.py \
  --input examples/data/few_proteins.fasta --output results/test/

# Run tests
mamba run -p ./env python -m pytest tests/ -v

# Run a single test file
mamba run -p ./env python -m pytest tests/test_basic.py -v

# Docker build and run
docker build -t esmfold_mcp .
docker run --gpus all esmfold_mcp

# Register as MCP server in Claude Code
claude mcp add esmfold -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

## Docker

The Dockerfile uses `pytorch/pytorch:2.4.0-cuda11.8-cudnn9-runtime` as base. It installs ESM from GitHub directly (not from `repo/`), sets `PYTHONPATH=/app`, and runs `src/server.py` as the default command. CI/CD via `.github/workflows/docker.yml` pushes to GHCR on main branch pushes.

## ESM-2 Models

Default model is `esm2_t33_650M_UR50D`. The `repr_layers` parameter must match the model's layer count (e.g., layer 33 for the 650M model, layer 6 for 8M). Use `esm2_t6_8M_UR50D` for fast testing.

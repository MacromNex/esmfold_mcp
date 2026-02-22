# ESMfold MCP Server

**Protein structure prediction using ESMFold via Docker**

An MCP (Model Context Protocol) server for ESMFold protein analysis with 5 core tools:
- Extract ESM-2 protein embeddings from sequences or FASTA files
- Submit large-scale embedding extraction jobs
- Batch process multiple FASTA files simultaneously
- Monitor and retrieve background job results
- Access server information and available models

## Quick Start with Docker

### Approach 1: Pull Pre-built Image from GitHub

The fastest way to get started. A pre-built Docker image is automatically published to GitHub Container Registry on every release.

```bash
# Pull the latest image
docker pull ghcr.io/macromnex/esmfold_mcp:latest

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add esmfold -- docker run -i --rm --user `id -u`:`id -g` --gpus all --ipc=host -v `pwd`:`pwd` ghcr.io/macromnex/esmfold_mcp:latest
```

**Note:** Run from your project directory. `` `pwd` `` expands to the current working directory.

**Requirements:**
- Docker with GPU support (`nvidia-docker` or Docker with NVIDIA runtime)
- Claude Code installed

That's it! The ESMfold MCP server is now available in Claude Code.

---

### Approach 2: Build Docker Image Locally

Build the image yourself and install it into Claude Code. Useful for customization or offline environments.

```bash
# Clone the repository
git clone https://github.com/MacromNex/esmfold_mcp.git
cd esmfold_mcp

# Build the Docker image
docker build -t esmfold_mcp:latest .

# Register with Claude Code (runs as current user to avoid permission issues)
claude mcp add esmfold -- docker run -i --rm --user `id -u`:`id -g` --gpus all --ipc=host -v `pwd`:`pwd` esmfold_mcp:latest
```

**Note:** Run from your project directory. `` `pwd` `` expands to the current working directory.

**Requirements:**
- Docker with GPU support
- Claude Code installed
- Git (to clone the repository)

**About the Docker Flags:**
- `-i` — Interactive mode for Claude Code
- `--rm` — Automatically remove container after exit
- `` --user `id -u`:`id -g` `` — Runs the container as your current user, so output files are owned by you (not root)
- `--gpus all` — Grants access to all available GPUs
- `--ipc=host` — Uses host IPC namespace for better performance
- `-v` — Mounts your project directory so the container can access your data

---

## Verify Installation

After adding the MCP server, you can verify it's working:

```bash
# List registered MCP servers
claude mcp list

# You should see 'esmfold' in the output
```

In Claude Code, you can now use all 5 ESMfold tools:
- `extract_protein_embeddings`
- `submit_protein_embeddings`
- `submit_batch_protein_embeddings`
- `get_job_status`
- `get_job_result`

---

## Next Steps

- **Detailed documentation**: See [detail.md](detail.md) for comprehensive guides on:
  - Available MCP tools and parameters
  - Local Python environment setup (alternative to Docker)
  - ESM-2 model selection guide
  - Example workflows and use cases
  - Output format options (NPZ, JSON)

---

## Usage Examples

Once registered, you can use the ESMfold tools directly in Claude Code. Here are some common workflows:

### Example 1: Extract Embeddings from FASTA

```
I have protein sequences in /path/to/proteins.fasta. Can you extract ESM-2 embeddings using extract_protein_embeddings with the esm2_t33_650M_UR50D model and save the embeddings to /path/to/embeddings/?
```

### Example 2: Large-Scale Embedding Extraction

```
I have a large dataset of 500 protein sequences in /path/to/large_dataset.fasta. Can you submit a batch embedding extraction job using submit_protein_embeddings with the esm2_t36_3B_UR50D model, then monitor the job until completion and retrieve the results?
```

### Example 3: Mutation Embedding Analysis

```
I have variant sequences in /path/to/variants.fasta for a mutational study. Can you extract embeddings for all variants using extract_protein_embeddings and save to /path/to/variant_embeddings/ so I can compare them?
```

---

## Troubleshooting

**Docker not found?**
```bash
docker --version  # Install Docker if missing
```

**GPU not accessible?**
- Ensure NVIDIA Docker runtime is installed
- Check with `docker run --gpus all ubuntu nvidia-smi`

**Claude Code not found?**
```bash
# Install Claude Code
npm install -g @anthropic-ai/claude-code
```

---

## License

Based on Meta AI Research (ESMFold/ESM-2)

# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: esmfold
- **Version**: 1.0.0
- **Created Date**: 2025-12-21
- **Server Path**: `src/server.py`
- **Environment**: Uses `env_esmfold` for ESM-2 protein embeddings
- **Dependencies**: fastmcp, loguru, ESM-2 (fair-esm), PyTorch

## Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and current status |
| `get_job_result` | Get completed job results |
| `get_job_log` | View job execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

## Sync Tools (Fast Operations < 10 min)

| Tool | Description | Source Script | Est. Runtime |
|------|-------------|---------------|--------------|
| `extract_protein_embeddings` | Extract ESM-2 protein embeddings | `scripts/protein_embeddings.py` | 30 sec - 2 min |
| `get_server_info` | Get server information and available models | Built-in | < 1 sec |

### Tool Details

#### extract_protein_embeddings
- **Description**: Extract protein sequence embeddings using ESM-2 language model
- **Source Script**: `scripts/protein_embeddings.py`
- **Estimated Runtime**: 30 seconds to 2 minutes (depending on model size and sequence count)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | No | None | Path to FASTA file with protein sequences |
| sequence | str | No | None | Single protein sequence (mutually exclusive with input_file) |
| output_dir | str | No | None | Directory to save embeddings |
| model | str | No | esm2_t33_650M_UR50D | ESM-2 model to use |
| repr_layers | List[int] | No | [33] | Layer numbers to extract representations from |
| include_per_tok | bool | No | False | Include per-residue token representations |
| include_bos | bool | No | False | Include beginning-of-sequence token |
| include_contacts | bool | No | False | Include attention-based contact predictions |
| device | str | No | auto | Device to use (auto, cuda, cpu) |
| format | str | No | npz | Output format (npz, json, both) |

**Available Models:**
- `esm2_t6_8M_UR50D` - 8M parameters (fastest)
- `esm2_t12_35M_UR50D` - 35M parameters
- `esm2_t30_150M_UR50D` - 150M parameters
- `esm2_t33_650M_UR50D` - 650M parameters (default)
- `esm2_t36_3B_UR50D` - 3B parameters (large)
- `esm2_t48_15B_UR50D` - 15B parameters (largest)

**Example:**
```
Use extract_protein_embeddings with input_file "examples/data/few_proteins.fasta" and output_dir "results/embeddings/"
```

#### get_server_info
- **Description**: Get information about the MCP server and available models
- **Source**: Built-in utility tool
- **Estimated Runtime**: < 1 second

**Parameters:** None

**Example:**
```
Use get_server_info to get server information
```

---

## Submit Tools (Long Operations > 10 min)

| Tool | Description | Source Script | Est. Runtime | Batch Support |
|------|-------------|---------------|--------------|---------------|
| `submit_protein_embeddings` | Submit protein embeddings extraction | `scripts/protein_embeddings.py` | Variable | ✅ Yes |
| `submit_batch_protein_embeddings` | Submit batch processing for multiple FASTA files | Custom batch script | Variable | ✅ Yes |

### Tool Details

#### submit_protein_embeddings
- **Description**: Submit protein embeddings extraction for background processing
- **Source Script**: `scripts/protein_embeddings.py`
- **Estimated Runtime**: Variable (use for large files, large models, or when you want to continue other work)
- **Supports Batch**: ✅ Yes (single FASTA with multiple sequences)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | No | None | Path to FASTA file with protein sequences |
| sequence | str | No | None | Single protein sequence (mutually exclusive with input_file) |
| output_dir | str | No | None | Directory to save embeddings |
| model | str | No | esm2_t33_650M_UR50D | ESM-2 model to use |
| repr_layers | List[int] | No | [33] | Layer numbers to extract representations from |
| include_per_tok | bool | No | False | Include per-residue token representations |
| include_bos | bool | No | False | Include beginning-of-sequence token |
| include_contacts | bool | No | False | Include attention-based contact predictions |
| device | str | No | auto | Device to use (auto, cuda, cpu) |
| format | str | No | npz | Output format (npz, json, both) |
| job_name | str | No | None | Custom job name for tracking |

**Example:**
```
Submit protein embeddings extraction for examples/data/P62593.fasta with model esm2_t36_3B_UR50D
```

#### submit_batch_protein_embeddings
- **Description**: Submit batch processing for multiple FASTA files
- **Source Script**: Dynamically generated batch script
- **Estimated Runtime**: Variable (depends on number of files and total sequences)
- **Supports Batch**: ✅ Yes (multiple separate FASTA files)

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_files | List[str] | Yes | - | List of FASTA file paths to process |
| output_dir | str | Yes | - | Directory to save all embeddings |
| model | str | No | esm2_t33_650M_UR50D | ESM-2 model to use |
| repr_layers | List[int] | No | [33] | Layer numbers to extract representations from |
| include_per_tok | bool | No | False | Include per-residue token representations |
| include_bos | bool | No | False | Include beginning-of-sequence token |
| include_contacts | bool | No | False | Include attention-based contact predictions |
| device | str | No | auto | Device to use (auto, cuda, cpu) |
| format | str | No | npz | Output format (npz, json, both) |
| job_name | str | No | None | Custom batch job name |

**Example:**
```
Submit batch protein embeddings for input_files ["examples/data/few_proteins.fasta", "examples/data/some_proteins.fasta"] with output_dir "results/batch/"
```

---

## Workflow Examples

### Quick Analysis (Sync)
```
Use extract_protein_embeddings with input_file "examples/data/few_proteins.fasta"
→ Returns results immediately (30 seconds - 2 minutes)
```

### Long-Running Task (Submit API)
```
1. Submit: Use submit_protein_embeddings with input_file "examples/data/P62593.fasta" and model "esm2_t48_15B_UR50D"
   → Returns: {"job_id": "abc123", "status": "submitted"}

2. Check: Use get_job_status with job_id "abc123"
   → Returns: {"status": "running", "started_at": "2025-12-21T09:30:00"}

3. Logs: Use get_job_log with job_id "abc123"
   → Returns: Recent log output from the job

4. Result: Use get_job_result with job_id "abc123" (when completed)
   → Returns: {"status": "success", "result": {...}}
```

### Batch Processing
```
Use submit_batch_protein_embeddings with input_files ["file1.fasta", "file2.fasta", "file3.fasta"] and output_dir "results/batch/"
→ Processes all files sequentially in a single job
→ Creates batch_results.json with per-file success/failure status
```

## Error Handling

All tools return structured error responses:

```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```

Common error scenarios:
- **File not found**: Invalid input file paths
- **Invalid input**: Mutually exclusive parameters used together
- **Job not found**: Invalid job_id provided
- **Import errors**: Missing dependencies (PyTorch, ESM)

## Environment Requirements

The MCP server uses different environments for different operations:

1. **MCP Server**: Uses `env` environment with fastmcp and loguru
2. **Protein Processing**: Uses `env_esmfold` environment via `mamba run` for ESM-2 operations

This separation allows the MCP server to run in a lightweight environment while delegating heavy computations to the specialized ESM environment.

## Performance Notes

### Model Selection Guidelines

| Model | Parameters | Speed | Use Case |
|-------|------------|-------|----------|
| esm2_t6_8M_UR50D | 8M | Fastest | Quick testing, many sequences |
| esm2_t33_650M_UR50D | 650M | Balanced | General use (default) |
| esm2_t48_15B_UR50D | 15B | Slowest | Best quality, research |

### When to Use Submit API
- Large FASTA files (>100 sequences)
- Large models (esm2_t36_3B_UR50D, esm2_t48_15B_UR50D)
- When you need to continue other work
- Batch processing multiple files

### Output Formats
- **NPZ**: Efficient binary format for numerical data
- **JSON**: Human-readable, larger file size
- **Both**: Maximum compatibility

## Job Persistence

Jobs persist across server restarts via the filesystem:
- Job metadata: `jobs/{job_id}/metadata.json`
- Job logs: `jobs/{job_id}/job.log`
- Job results: `jobs/{job_id}/output.json`

## Testing

Basic functionality tests:
```bash
# Test server import and startup
PYTHONPATH=src:scripts mamba run -p ./env python tests/test_basic.py

# Test server startup (should show FastMCP banner)
PYTHONPATH=src:scripts mamba run -p ./env python src/server.py
```
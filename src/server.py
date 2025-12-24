#!/usr/bin/env python3
"""MCP Server for ESMFold

Provides both synchronous and asynchronous (submit) APIs for protein analysis tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys
import subprocess
import json

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("esmfold")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def extract_protein_embeddings(
    input_file: Optional[str] = None,
    sequence: Optional[str] = None,
    output_dir: Optional[str] = None,
    model: str = "esm2_t33_650M_UR50D",
    repr_layers: List[int] = None,
    include_per_tok: bool = False,
    include_bos: bool = False,
    include_contacts: bool = False,
    device: str = "auto",
    format: str = "npz"
) -> dict:
    """
    Extract protein sequence embeddings using ESM-2 language model.

    This is a synchronous operation that typically completes in 30 seconds to 2 minutes
    depending on the model size and number of sequences.

    Args:
        input_file: Path to FASTA file with protein sequences (optional)
        sequence: Single protein sequence string (optional, mutually exclusive with input_file)
        output_dir: Directory to save embeddings (optional, uses temp if not provided)
        model: ESM-2 model to use (esm2_t6_8M_UR50D to esm2_t48_15B_UR50D)
        repr_layers: List of layer numbers to extract representations from (default: [33])
        include_per_tok: Include per-residue token representations
        include_bos: Include beginning-of-sequence token
        include_contacts: Include attention-based contact predictions
        device: Device to use (auto, cuda, cpu)
        format: Output format (npz, json, both)

    Returns:
        Dictionary with embeddings results and output file paths
    """
    # Import the script's main function
    try:
        from protein_embeddings import run_protein_embeddings
    except ImportError as e:
        return {"status": "error", "error": f"Failed to import script: {e}"}

    # Validate inputs
    if not input_file and not sequence:
        return {"status": "error", "error": "Either input_file or sequence must be provided"}

    if input_file and sequence:
        return {"status": "error", "error": "input_file and sequence are mutually exclusive"}

    # Set default repr_layers if not provided
    if repr_layers is None:
        repr_layers = [33]

    try:
        result = run_protein_embeddings(
            input_file=input_file,
            sequence=sequence,
            output_dir=output_dir,
            config={
                "model_name": model,
                "repr_layers": repr_layers,
                "include_per_tok": include_per_tok,
                "include_bos": include_bos,
                "include_contacts": include_contacts,
                "device": device,
                "output_format": format
            }
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"extract_protein_embeddings failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_protein_embeddings(
    input_file: Optional[str] = None,
    sequence: Optional[str] = None,
    output_dir: Optional[str] = None,
    model: str = "esm2_t33_650M_UR50D",
    repr_layers: List[int] = None,
    include_per_tok: bool = False,
    include_bos: bool = False,
    include_contacts: bool = False,
    device: str = "auto",
    format: str = "npz",
    job_name: Optional[str] = None
) -> dict:
    """
    Submit protein embeddings extraction for background processing.

    Use this for large FASTA files, large models (esm2_t36_3B_UR50D, esm2_t48_15B_UR50D),
    or when you want to continue other work while processing.

    Args:
        input_file: Path to FASTA file with protein sequences (optional)
        sequence: Single protein sequence string (optional, mutually exclusive with input_file)
        output_dir: Directory to save embeddings
        model: ESM-2 model to use (esm2_t6_8M_UR50D to esm2_t48_15B_UR50D)
        repr_layers: List of layer numbers to extract representations from (default: [33])
        include_per_tok: Include per-residue token representations
        include_bos: Include beginning-of-sequence token
        include_contacts: Include attention-based contact predictions
        device: Device to use (auto, cuda, cpu)
        format: Output format (npz, json, both)
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    # Validate inputs
    if not input_file and not sequence:
        return {"status": "error", "error": "Either input_file or sequence must be provided"}

    if input_file and sequence:
        return {"status": "error", "error": "input_file and sequence are mutually exclusive"}

    script_path = str(SCRIPTS_DIR / "protein_embeddings.py")

    # Build arguments
    args = {
        "model": model,
        "device": device,
        "format": format
    }

    if input_file:
        args["input"] = input_file
    if sequence:
        args["sequence"] = sequence
    if output_dir:
        args["output"] = output_dir
    if repr_layers is not None:
        args["repr-layers"] = ','.join(map(str, repr_layers))
    if include_per_tok:
        args["include-per-tok"] = ""
    if include_bos:
        args["include-bos"] = ""
    if include_contacts:
        args["include-contacts"] = ""

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"embeddings_{model}"
    )

# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_protein_embeddings(
    input_files: List[str],
    output_dir: str,
    model: str = "esm2_t33_650M_UR50D",
    repr_layers: List[int] = None,
    include_per_tok: bool = False,
    include_bos: bool = False,
    include_contacts: bool = False,
    device: str = "auto",
    format: str = "npz",
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch protein embeddings extraction for multiple FASTA files.

    Processes multiple FASTA files in sequence within a single job. Useful for:
    - Processing many protein sequence files at once
    - Large-scale analysis
    - Consistent parameters across multiple files

    Args:
        input_files: List of FASTA file paths to process
        output_dir: Directory to save all embeddings
        model: ESM-2 model to use (esm2_t6_8M_UR50D to esm2_t48_15B_UR50D)
        repr_layers: List of layer numbers to extract representations from (default: [33])
        include_per_tok: Include per-residue token representations
        include_bos: Include beginning-of-sequence token
        include_contacts: Include attention-based contact predictions
        device: Device to use (auto, cuda, cpu)
        format: Output format (npz, json, both)
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    if not input_files:
        return {"status": "error", "error": "input_files list cannot be empty"}

    # Create a batch script that processes each file
    batch_script_content = f'''#!/usr/bin/env python3
"""Batch processing script for protein embeddings."""

import sys
import subprocess
from pathlib import Path

input_files = {input_files}
output_dir = "{output_dir}"
model = "{model}"
repr_layers = {repr_layers or [33]}
device = "{device}"
format = "{format}"
include_per_tok = {include_per_tok}
include_bos = {include_bos}
include_contacts = {include_contacts}

results = []

for i, input_file in enumerate(input_files, 1):
    print(f"Processing file {{i}}/{{len(input_files)}}: {{input_file}}")

    cmd = [
        "mamba", "run", "-p", "./env_esmfold", "python", "scripts/protein_embeddings.py",
        "--input", input_file,
        "--output", output_dir,
        "--model", model,
        "--repr-layers", ",".join(map(str, repr_layers)),
        "--device", device,
        "--format", format
    ]

    if include_per_tok:
        cmd.append("--include-per-tok")
    if include_bos:
        cmd.append("--include-bos")
    if include_contacts:
        cmd.append("--include-contacts")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            results.append({{"file": input_file, "status": "success"}})
            print(f"✓ Successfully processed {{input_file}}")
        else:
            results.append({{"file": input_file, "status": "failed", "error": result.stderr}})
            print(f"✗ Failed to process {{input_file}}: {{result.stderr}}")
    except Exception as e:
        results.append({{"file": input_file, "status": "failed", "error": str(e)}})
        print(f"✗ Exception processing {{input_file}}: {{e}}")

# Save batch results
import json
with open("{output_dir}/batch_results.json", "w") as f:
    json.dump({{"batch_results": results, "total_files": len(input_files)}}, f, indent=2)

print(f"Batch processing complete. Results saved to {output_dir}/batch_results.json")
'''

    # Save batch script
    batch_script_dir = MCP_ROOT / "temp_scripts"
    batch_script_dir.mkdir(exist_ok=True)
    batch_script_path = batch_script_dir / f"batch_embeddings_{len(input_files)}_files.py"

    with open(batch_script_path, 'w') as f:
        f.write(batch_script_content)

    return job_manager.submit_job(
        script_path=str(batch_script_path),
        args={},
        job_name=job_name or f"batch_{len(input_files)}_files"
    )

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def get_server_info() -> dict:
    """
    Get information about the MCP server and available models.

    Returns:
        Dictionary with server information and available models
    """
    return {
        "status": "success",
        "server_name": "esmfold",
        "version": "1.0.0",
        "description": "ESMFold MCP Server for protein analysis",
        "available_models": [
            "esm2_t6_8M_UR50D",      # 8M parameters - fastest
            "esm2_t12_35M_UR50D",    # 35M parameters
            "esm2_t30_150M_UR50D",   # 150M parameters
            "esm2_t33_650M_UR50D",   # 650M parameters - default
            "esm2_t36_3B_UR50D",     # 3B parameters - large
            "esm2_t48_15B_UR50D"     # 15B parameters - largest
        ],
        "tools": {
            "sync": ["extract_protein_embeddings", "get_server_info"],
            "async": ["submit_protein_embeddings", "submit_batch_protein_embeddings"],
            "job_management": ["get_job_status", "get_job_result", "get_job_log", "cancel_job", "list_jobs"]
        },
        "example_data": str(MCP_ROOT / "examples" / "data")
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()
# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-21
- **Filter Applied**: Protein structure prediction using ESMFold
- **Python Version Strategy**: Dual environment (3.10 + 3.7)
- **Environment Strategy**: dual (main + legacy)

## Use Cases Identified and Implemented

### UC-001: Single Protein Structure Prediction
- **Description**: Predict 3D structure for individual protein sequences using ESMFold
- **Script Path**: `examples/use_case_1_single_protein_folding.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env_py3.7`
- **Source**: README.md ESMFold section, scripts/fold.py

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Single protein amino acid sequence | --sequence |
| input_file | file | FASTA file with protein sequences | --input |
| output_path | string | Output PDB file or directory | --output |
| chunk_size | integer | Memory optimization chunk size | --chunk-size |
| cpu_only | flag | Force CPU usage | --cpu-only |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| pdb_file | file | 3D structure in PDB format |
| confidence | float | pLDDT confidence score (0-100) |

**Example Usage:**
```bash
mamba run -p ./env_py3.7 python examples/use_case_1_single_protein_folding.py --sequence MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG --output protein.pdb
```

**Example Data**: `examples/data/few_proteins.fasta`

---

### UC-002: Batch Structure Prediction
- **Description**: Efficient batch processing of multiple proteins with memory optimization
- **Script Path**: `examples/use_case_2_batch_structure_prediction.py`
- **Complexity**: complex
- **Priority**: high
- **Environment**: `./env_py3.7`
- **Source**: scripts/fold.py batching functionality

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | FASTA file with multiple sequences | --input, -i |
| output_dir | string | Directory for output PDB files | --output, -o |
| max_tokens_per_batch | integer | Maximum tokens per batch (default: 1024) | --max-tokens-per-batch |
| num_recycles | integer | Number of structure refinement cycles | --num-recycles |
| chunk_size | integer | Axial attention chunk size | --chunk-size |
| cpu_only | flag | Force CPU usage | --cpu-only |
| cpu_offload | flag | Enable CPU offloading for large sequences | --cpu-offload |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| pdb_files | files | Multiple PDB structure files |
| batch_report | text | Prediction summary and statistics |

**Example Usage:**
```bash
mamba run -p ./env_py3.7 python examples/use_case_2_batch_structure_prediction.py --input examples/data/some_proteins.fasta --output results/ --max-tokens-per-batch 512
```

**Example Data**: `examples/data/some_proteins.fasta`

---

### UC-003: Protein Sequence Embeddings
- **Description**: Extract protein sequence embeddings using ESM-2 language models
- **Script Path**: `examples/use_case_3_protein_embeddings.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env_py3.7`
- **Source**: README.md ESM-2 examples, scripts/extract.py

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Single protein sequence | --sequence |
| input_file | file | FASTA file with sequences | --input |
| output_dir | string | Directory for embedding files | --output |
| model | string | ESM-2 model size to use | --model |
| repr_layers | list | Representation layers to extract | --repr-layers |
| format | string | Output format (npz, pt, txt) | --format |
| include_per_tok | flag | Include per-residue embeddings | --include-per-tok |
| include_contacts | flag | Include attention-based contacts | --include-contacts |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| embeddings | files | Sequence embeddings in specified format |
| analysis | text | Basic embedding statistics |

**Example Usage:**
```bash
mamba run -p ./env_py3.7 python examples/use_case_3_protein_embeddings.py --input examples/data/few_proteins.fasta --output embeddings/ --include-per-tok
```

**Example Data**: `examples/data/P62593.fasta`

---

### UC-004: Multimer Structure Prediction
- **Description**: Predict structures for protein complexes with multiple chains
- **Script Path**: `examples/use_case_4_multimer_prediction.py`
- **Complexity**: complex
- **Priority**: medium
- **Environment**: `./env_py3.7`
- **Source**: README.md multimer examples

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| chains | string | Protein sequences separated by colons | --chains |
| input_file | file | FASTA with multimer sequences | --input |
| output_path | string | Output PDB file or directory | --output |
| chunk_size | integer | Memory optimization for large complexes | --chunk-size |
| analyze_interfaces | flag | Perform basic interface analysis | --analyze-interfaces |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| pdb_file | file | Multi-chain structure in PDB format |
| interface_analysis | text | Chain interaction summary |
| per_chain_confidence | dict | pLDDT scores for each chain |

**Example Usage:**
```bash
mamba run -p ./env_py3.7 python examples/use_case_4_multimer_prediction.py --chains "MKTVRQERLKSIVRIL...:ARTKQTARKSTGGKAP..." --output complex.pdb
```

**Example Data**: `examples/data/4uv3.pdb` (reference complex structure)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Use Cases Found | 4 |
| Scripts Created | 4 |
| High Priority | 3 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Copied | ✅ |

## Demo Data Index

| Source | Destination | Description | Size |
|--------|-------------|-------------|------|
| `repo/esm/examples/data/few_proteins.fasta` | `examples/data/few_proteins.fasta` | 3 short protein sequences for testing | 319 B |
| `repo/esm/examples/data/some_proteins.fasta` | `examples/data/some_proteins.fasta` | ~20 protein sequences for batch testing | 5.4 KB |
| `repo/esm/examples/data/P62593.fasta` | `examples/data/P62593.fasta` | Large protein sequence collection | 1.7 MB |
| `repo/esm/examples/inverse_folding/data/5YH2.pdb` | `examples/data/5YH2.pdb` | Reference protein structure | 1.2 MB |
| `repo/esm/examples/inverse_folding/data/4uv3.pdb` | `examples/data/4uv3.pdb` | Multi-chain protein complex | 2.9 MB |
| `repo/esm/examples/inverse_folding/data/5YH2_mutated_seqs.fasta` | `examples/data/5YH2_mutated_seqs.fasta` | Variant sequences for analysis | 1.6 KB |
| Various MSA files | `examples/data/*.a3m` | Multiple sequence alignments | Various |

## Technical Implementation Details

### Memory Optimization Features
- Chunked attention computation (chunk sizes: 128, 64, 32)
- Sequence batching by length for efficient GPU utilization
- CPU offloading for large sequences
- Automatic fallback to CPU when GPU memory is insufficient

### Error Handling
- CUDA out of memory detection and recovery
- Graceful degradation to CPU mode
- Detailed error logging and troubleshooting suggestions
- Input validation and format checking

### Performance Optimizations
- Intelligent batching strategies
- Progress tracking and timing metrics
- Memory usage monitoring
- Support for various model sizes (8M to 15B parameters)

### Output Formats
- PDB structures with pLDDT confidence scores
- NumPy compressed arrays (.npz)
- PyTorch tensors (.pt)
- Plain text embeddings (.txt)
- Detailed logs and analysis reports

## Integration Readiness

All use cases are designed as standalone, well-documented Python scripts that can be easily integrated into MCP tools. Each script includes:

- Comprehensive command-line interface
- Detailed help and usage information
- Error handling and recovery mechanisms
- Support for both single sequences and batch processing
- Memory optimization options
- Progress reporting and logging
- Example usage and test data

The scripts serve as the foundation for MCP tools that will provide protein structure prediction capabilities to Claude and other AI applications.
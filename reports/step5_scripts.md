# Step 5: Scripts Extraction Report

## Extraction Information
- **Extraction Date**: 2025-12-21
- **Total Scripts**: 1
- **Fully Independent**: 0
- **Repo Dependent**: 1
- **Inlined Functions**: 3
- **Config Files Created**: 1
- **Shared Library Modules**: 2

## Extraction Summary

Based on Step 4 execution results, only 1 out of 4 use cases worked successfully (UC-003: Protein Sequence Embeddings). The other 3 use cases failed due to PyTorch version compatibility issues between ESM environment (PyTorch 1.12.1) and OpenFold requirements (PyTorch ≥1.13).

## Scripts Overview

| Script | Description | Independent | Config |
|--------|-------------|-------------|--------|
| `protein_embeddings.py` | Extract ESM-2 protein sequence embeddings | ❌ No (fair-esm) | `configs/protein_embeddings_config.json` |

---

## Script Details

### protein_embeddings.py
- **Path**: `scripts/protein_embeddings.py`
- **Source**: `examples/use_case_3_protein_embeddings.py`
- **Description**: Extract protein sequence embeddings using ESM-2 language model
- **Main Function**: `run_protein_embeddings(input_file=None, sequence=None, output_dir=None, config=None, **kwargs)`
- **Config File**: `configs/protein_embeddings_config.json`
- **Tested**: ✅ Yes
- **Independent of Repo**: ❌ No

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | argparse, sys, pathlib, typing, json, numpy, torch |
| Repo Required | fair-esm package (installed from repo/esm) |
| Inlined | `read_fasta()`, `load_esm_model()`, `save_embeddings_*()` |

**Repo Dependencies Reason**: Requires fair-esm package which was installed from the local ESM repository. The package is not available via standard PyPI, so it depends on the local repo installation.

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | fasta | FASTA file with protein sequences (optional) |
| sequence | string | - | Single protein sequence (optional, mutually exclusive with input_file) |
| output_dir | string | - | Output directory path (optional) |
| config | dict | json | Configuration dictionary (optional) |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| embeddings | dict | - | Extracted embeddings by sequence label |
| output_files | list | - | List of saved file paths |
| metadata | dict | - | Execution metadata |

**CLI Usage:**
```bash
python scripts/protein_embeddings.py --input FILE --output DIR [OPTIONS]
python scripts/protein_embeddings.py --sequence "PROTEIN_SEQ" --output DIR [OPTIONS]
```

**CLI Options:**
- `--model`: ESM-2 model (esm2_t6_8M_UR50D to esm2_t48_15B_UR50D)
- `--repr-layers`: Layer numbers to extract (default: [33])
- `--include-per-tok`: Include per-residue representations
- `--include-bos`: Include beginning-of-sequence token
- `--include-contacts`: Include attention contacts
- `--device`: Computation device (auto, cuda, cpu)
- `--format`: Output format (npz, json, both)
- `--config`: JSON config file path

**Examples:**
```bash
# FASTA file input
python scripts/protein_embeddings.py --input examples/data/few_proteins.fasta --output results/embeddings/

# Single sequence
python scripts/protein_embeddings.py --sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" --output results/single/

# With options
python scripts/protein_embeddings.py --input FILE --output DIR --model esm2_t6_8M_UR50D --include-per-tok --format both

# With config
python scripts/protein_embeddings.py --input FILE --output DIR --config configs/protein_embeddings_config.json
```

**Testing Results:**
- ✅ Works with FASTA files (3 sequences)
- ✅ Works with single sequences
- ✅ Generates NPZ and JSON output formats
- ✅ Produces embeddings with correct dimensions (1280-d vectors)
- ✅ Handles different sequence lengths (65-99 residues tested)
- ✅ Works in CPU-only mode (env_esmfold)

---

## Configuration Files

### configs/protein_embeddings_config.json
- **Description**: Configuration for ESM-2 protein embeddings extraction
- **Presets**: 4 presets (fast, standard, detailed, research)
- **Model Options**: All 6 ESM-2 model variants
- **Output Options**: NPZ, JSON, both formats
- **MCP Defaults**: Optimized settings for MCP tool usage

**Key Sections:**
- `model`: Model selection and alternatives
- `extraction`: Layer and representation options
- `computation`: Device and batch size settings
- `output`: Format and metadata options
- `presets`: Pre-configured option sets
- `mcp_defaults`: Default settings for MCP integration

---

## Shared Library

**Path**: `scripts/lib/`

| Module | Functions | Description |
|--------|-----------|-------------|
| `io.py` | 4 functions | File I/O, FASTA reading, filename cleaning |
| `utils.py` | 6 functions | Sequence validation, header parsing, memory estimation |

**Total Functions**: 10

### scripts/lib/io.py
- `load_json()`: Load JSON configuration files
- `save_json()`: Save results to JSON
- `read_fasta()`: Parse FASTA files (inlined from esm.data)
- `clean_filename()`: Sanitize filenames for safe saving

### scripts/lib/utils.py
- `validate_sequence()`: Check protein sequence validity
- `clean_sequence()`: Remove invalid amino acid characters
- `parse_sequence_header()`: Extract metadata from FASTA headers
- `chunk_list()`: Split lists into chunks
- `estimate_memory_usage()`: Estimate ESM model memory requirements

---

## Extraction Process

### 1. Dependency Analysis
From `examples/use_case_3_protein_embeddings.py`:
- **Essential imports**: 5 packages (argparse, sys, torch, numpy, pathlib)
- **ESM imports**: 2 functions (esm, esm.data.read_fasta)
- **Local functions**: 4 major functions extracted

### 2. Function Inlining
**Inlined Functions:**
1. `read_fasta()` - Originally from esm.data.read_fasta
   - **Reason**: Simple file parser, reduce ESM dependency
   - **Lines reduced**: From import to 45-line standalone function

2. `save_embeddings()` - Extracted and simplified
   - **Reason**: Original had 3 format options, simplified to NPZ/JSON
   - **Added**: Metadata saving, better error handling

3. `analyze_embeddings()` - Integrated into main function
   - **Reason**: Analysis was for display only, integrated into return values
   - **Benefit**: Cleaner API for MCP usage

**Lazy Loading:**
- ESM model loading isolated to `load_esm_model()` function
- Imports happen only when needed, with clear error messages

### 3. Configuration Externalization
**Moved to config:**
- Model selection (6 ESM-2 variants)
- Layer extraction options
- Representation types (mean, per-token, contacts)
- Output format preferences
- Device selection logic

### 4. MCP Optimization
**Main Function Design:**
```python
def run_protein_embeddings(
    input_file: Optional[Union[str, Path]] = None,
    sequence: Optional[str] = None,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
```

**Return Format:**
- `embeddings`: Dictionary of sequence embeddings
- `output_files`: List of saved files (if any)
- `metadata`: Execution information

This design is ready for MCP tool wrapping with clear inputs/outputs.

---

## Failed Use Cases Analysis

### Why Other Use Cases Weren't Extracted

| Use Case | Status | Issue | Solution Required |
|----------|--------|-------|-------------------|
| UC-001: Single Protein Folding | ❌ Failed | PyTorch 1.12.1 vs OpenFold requiring ≥1.13 | Upgrade to Python 3.8+ environment |
| UC-002: Batch Structure Prediction | ❌ Failed | Same PyTorch compatibility issue | Upgrade to Python 3.8+ environment |
| UC-004: Multimer Prediction | ❌ Failed | Same PyTorch compatibility issue | Upgrade to Python 3.8+ environment |

**Root Cause**: ESM's environment.yml specifies Python 3.7 and PyTorch 1.12.*, but OpenFold (required for ESMFold structure prediction) requires PyTorch ≥1.13, which isn't available for Python 3.7.

**Potential Solutions:**
1. **Environment Upgrade**: Create Python 3.8+ environment with PyTorch 1.13+
2. **Alternative Implementation**: Use ColabFold or other structure prediction methods
3. **Docker Approach**: Use official ESMFold containers
4. **Stub Implementation**: Create placeholder functions that return error messages

---

## Environment Details

### Working Environment: `env_esmfold`
```bash
# Key packages:
- Python: 3.7.12
- PyTorch: 1.12.1+cpu
- fair-esm: 2.0.1 (from source at repo/esm)
- einops: 0.6.1 (downgraded for Python 3.7 compatibility)
- NumPy: 1.19.5
```

### Testing Commands
```bash
# Activate environment
mamba activate ./env_esmfold

# Test with FASTA file
python scripts/protein_embeddings.py --input examples/data/few_proteins.fasta --output results/test_embeddings/

# Test with single sequence
python scripts/protein_embeddings.py --sequence "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG" --output results/test_single/

# Test different formats
python scripts/protein_embeddings.py --sequence "ACDEFGHIKLMNPQRSTVWY" --output results/formats/ --format both
```

---

## File Structure Created

### Scripts Directory: `scripts/`
```
scripts/
├── lib/
│   ├── __init__.py          # Shared library imports
│   ├── io.py               # File I/O utilities
│   └── utils.py            # Sequence and general utilities
├── protein_embeddings.py   # Clean ESM-2 embeddings script
└── README.md               # Usage documentation
```

### Configuration Directory: `configs/`
```
configs/
└── protein_embeddings_config.json  # ESM-2 configuration with presets
```

### Results Generated: `results/`
```
results/
├── test_embeddings/        # FASTA file test results
│   ├── UniRef50_UPI0003108055.npz
│   ├── UniRef50_A0A223SCH7.npz
│   └── UniRef50_A0A090SUK6.npz
├── test_single/            # Single sequence test
│   ├── metadata/
│   │   └── single_sequence.json
│   └── single_sequence.npz
└── test_independent/       # Independence test (would fail without repo)
```

---

## Success Criteria Assessment

- [x] All verified use cases have corresponding scripts (1/1 working use case)
- [x] Each script has a clearly defined main function (`run_protein_embeddings()`)
- [x] Dependencies are minimized - only essential imports + fair-esm
- [x] Repo-specific code is inlined (FASTA reading, model loading)
- [x] Configuration is externalized to `configs/` directory
- [x] Scripts work with example data
- [x] `reports/step5_scripts.md` documents all scripts with dependencies
- [x] Scripts are tested and produce correct outputs
- [x] README.md in `scripts/` explains usage

## Dependency Summary

### Minimized Dependencies Achieved:
- ✅ Inlined FASTA reading (was esm.data.read_fasta)
- ✅ Simplified model loading with better error handling
- ✅ Consolidated analysis functions
- ✅ Externalized all configuration

### Remaining Dependencies:
- ❌ fair-esm package (requires repo/esm installation)
  - **Reason**: Not available on PyPI, must be installed from source
  - **Impact**: Script is not fully independent but minimizes ESM ecosystem dependencies

### For MCP Usage:
The script is ready for MCP wrapping despite the fair-esm dependency because:
1. Clear function interface with documented inputs/outputs
2. Proper error handling and validation
3. Configuration via JSON files
4. Minimal API surface area
5. Predictable behavior and return values

---

## Recommendations

### Immediate Actions
1. **Use `protein_embeddings.py`** for MCP tool development
2. **Include fair-esm installation** in MCP setup documentation
3. **Test with various sequence types** before production deployment

### Future Enhancements
1. **Add more models**: Consider other protein language models
2. **Batch processing**: Optimize for multiple sequences
3. **Memory management**: Add automatic chunking for large sequences
4. **Alternative structure prediction**: Implement ColabFold-based folding

### Step 6 Preparation
The script is ready for MCP tool wrapping:
```python
# MCP tool wrapper preview
@mcp.tool()
def extract_protein_embeddings(
    input_file: str = None,
    sequence: str = None,
    output_dir: str = None,
    model_name: str = "esm2_t33_650M_UR50D"
):
    return run_protein_embeddings(
        input_file=input_file,
        sequence=sequence,
        output_dir=output_dir,
        model_name=model_name
    )
```

---

## Notes

The extraction process successfully created a clean, configurable, and MCP-ready script from the one working use case. While full independence from the repo wasn't achieved due to the fair-esm package requirement, the script represents a significant simplification and optimization for MCP usage compared to the original example code.

The failure of the other use cases due to PyTorch version conflicts highlights the importance of environment management in protein modeling tools. For production use, consider upgrading to a more recent Python/PyTorch environment or using containerized solutions.
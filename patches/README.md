# Patches Directory

This directory contains patches and documentation for issues found during use case execution.

## ESMFold PyTorch Compatibility Issue

### Problem
The ESMFold functionality (UC-001, UC-002, UC-004) fails due to a PyTorch version compatibility issue:

```
Error: cannot import name 'is_fx_tracing' from 'torch.fx._symbolic_trace'
```

### Root Cause
- ESMFold requires OpenFold as a dependency
- OpenFold expects a newer PyTorch version (≥1.13) with the `is_fx_tracing` function
- The ESM environment specification requires PyTorch 1.12.*
- Python 3.7 support is limited for newer PyTorch versions

### Environment Details
- **Python**: 3.7.12
- **PyTorch**: 1.12.1+cpu
- **ESM**: 2.0.1
- **OpenFold**: 2.2.0
- **einops**: 0.6.1 (downgraded from 0.7.0 for Python 3.7 compatibility)

### Attempted Solutions
1. ✅ Fixed initial PyTorch import issues (Intel VTune symbol conflicts)
2. ✅ Installed CPU-only PyTorch to avoid CUDA conflicts
3. ✅ Downgraded einops for Python 3.7 compatibility
4. ✅ Installed missing dependencies (openfold, modelcif)
5. ❌ PyTorch version upgrade blocked by Python 3.7 constraints

### Working Use Cases
- **UC-003: Protein Sequence Embeddings** ✅ - Uses ESM-2 language model only, no ESMFold

### Blocked Use Cases
- **UC-001: Single Protein Structure Prediction** ❌ - Requires ESMFold
- **UC-002: Batch Structure Prediction** ❌ - Requires ESMFold
- **UC-004: Multimer Structure Prediction** ❌ - Requires ESMFold

### Recommended Solutions

#### Option 1: Use Python 3.8+ Environment
Create a new environment with Python 3.8+ and PyTorch 1.13+:
```bash
mamba create -p ./env_py38 python=3.8 pytorch=1.13 -c pytorch
```

#### Option 2: Alternative ESM Implementation
Use simpler ESM models without OpenFold dependency for structure prediction.

#### Option 3: Docker Container
Use the official ESMFold Docker container which has all dependencies pre-configured.

### Impact
- 75% of use cases (3/4) are blocked by this dependency issue
- Only embeddings functionality is working
- MCP tool development can proceed with embeddings but structure prediction needs environment upgrade
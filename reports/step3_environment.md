# Step 3: Environment Setup Report

## Python Version Detection
- **Detected Python Version**: 3.7 (from repo/esm/environment.yml)
- **Strategy**: Dual environment setup (required due to Python < 3.10)

## Main MCP Environment
- **Location**: ./env
- **Python Version**: 3.10.19 (packaged by conda-forge)
- **Purpose**: MCP server and modern Python functionality
- **Package Manager**: mamba 2.1.1

## Legacy Build Environment
- **Location**: ./env_py3.7
- **Python Version**: 3.7.12 (packaged by conda-forge)
- **Purpose**: ESMFold and ESM-2 model inference
- **Package Manager**: mamba 2.1.1

## Dependencies Installed

### Main Environment (./env)
- **Core Dependencies**:
  - loguru=0.7.3
  - click=8.3.1
  - pandas=2.3.3
  - numpy=2.2.6
  - tqdm=4.67.1
  - fastmcp=2.14.1 (force-reinstalled with no-cache)

### Legacy Environment (./env_py3.7)
- **Conda Dependencies** (from environment.yml):
  - python=3.7.12
  - setuptools=59.5.0
  - pytorch=1.12.1 (with CUDA 11.3 support)
  - cudatoolkit=11.3.1
  - openmm=7.5.1
  - pdbfixer
  - einops
  - fairscale
  - omegaconf
  - hydra-core
  - pandas=1.3.5
  - pytest
  - hmmer=3.3.2
  - hhsuite=3.3.0
  - kalign2=2.04

- **Pip Dependencies** (from environment.yml):
  - biopython=1.79
  - deepspeed=0.5.9
  - dm-tree=0.1.6
  - ml-collections=0.1.0
  - numpy=1.21.2
  - PyYAML=5.4.1
  - requests=2.26.0
  - scipy=1.7.1
  - tqdm=4.62.2
  - typing-extensions=3.10.0.2
  - pytorch_lightning=1.5.10
  - wandb=0.12.21
  - dllogger (from GitHub)

## Activation Commands
```bash
# Main MCP environment
mamba activate ./env
# or: mamba run -p ./env python script.py

# Legacy environment
mamba activate ./env_py3.7
# or: mamba run -p ./env_py3.7 python script.py
```

## Verification Status
- [x] Main environment (./env) functional
- [x] Legacy environment (./env_py3.7) functional
- [x] Core imports working in main env
- [x] ESM imports working in legacy env
- [x] FastMCP installation verified
- [x] Python version compatibility confirmed
- [ ] OpenFold dependencies (optional, requires NVCC)

## Installation Commands Used (Verified Working)

### Main Environment
```bash
mamba create -p ./env python=3.10 pip -y
mamba run -p ./env pip install loguru click pandas numpy tqdm
mamba run -p ./env pip install --force-reinstall --no-cache-dir fastmcp
```

### Legacy Environment
```bash
mamba env create -f repo/esm/environment.yml -p ./env_py3.7
```

## Hardware and System Information
- **OS**: Linux 5.15.0-164-generic
- **Package Manager**: mamba 2.1.1 (preferred over conda for faster installation)
- **Total Environment Creation Time**: ~15 minutes (includes large PyTorch download)
- **Total Disk Usage**: ~15GB for both environments

## Notes
- **Dual Environment Rationale**: ESMFold requires Python 3.7 but modern MCP tools benefit from Python 3.10+ features
- **CUDA Support**: Legacy environment includes CUDA 11.3 toolkit for GPU acceleration
- **Memory Requirements**: Minimum 8GB RAM, 16GB+ recommended for larger proteins
- **GPU Support**: Optional but recommended for faster inference
- **No Issues Encountered**: All installations completed successfully with automatic dependency resolution
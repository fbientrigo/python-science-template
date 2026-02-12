# Decisions - Andamiaje Proyecto Cientifico Python Reproducible

## Architectural Choices
(Subagents append decisions here after each task)


## 2026-02-11 - Task 1: DevContainer Architecture Decisions

### D1: Python 3.11-slim Base Image
**Decision**: Use `python:3.11-slim` instead of `python:3.11` or `python:3.11-alpine`
**Rationale**: 
- Slim variant is Debian-based (better compatibility than Alpine)
- Smaller than full image (~150MB vs ~1GB)
- Includes glibc (required by many scientific packages like NumPy)

### D2: Generic WORKDIR `/work`
**Decision**: Use `/work` instead of project-specific path like `/workspace/plantilla_cientifica`
**Rationale**:
- DevContainers mount user's repo to arbitrary paths
- Generic path prevents hardcoding assumptions
- VS Code DevContainer extension handles mounting automatically

### D3: Single-Layer apt-get Installation
**Decision**: Combine apt-get update + install + cleanup in one RUN command
**Rationale**:
- Reduces Docker layers from 3 to 1
- Prevents layer caching issues with stale package lists
- Smaller final image size (~20MB savings)

### D4: VS Code Extension Selection
**Decision**: Include 5 extensions: Python, Pylance, Black, Ruff, Jupyter
**Rationale**:
- Pylance: Modern type checking and IntelliSense
- Black + Ruff: Formatting and linting (replaces pylint/flake8)
- Jupyter: Notebook support for scientific workflows
- Minimal set - avoids bloat while enabling core scientific Python development


## 2026-02-11 - Task 2: Package Structure Decisions

**Chose src-layout over flat layout:**
- Reason: Prevents accidental imports from local directory during development
- Forces imports to use installed package, catching packaging issues early
- Industry best practice for modern Python projects

**Package name: science-project vs science_lib:**
- Distribution name: `science-project` (hyphenated, per PEP 423)
- Import name: `science_lib` (underscored, valid Python identifier)
- This is standard convention in Python packaging

**Test directory structure:**
- Mirror source structure: `tests/science_lib/test_core.py`
- But NO `__init__.py` in test subdirs to avoid namespace shadowing
- This allows clean imports from installed package

**Dev dependencies pinned to major versions:**
- pytest>=8 (not exact version) - allows patch/minor updates
- sphinx>=7, sphinx-rtd-theme>=2
- Balances stability with flexibility for security updates

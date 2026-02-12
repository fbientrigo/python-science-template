# Learnings - Andamiaje Proyecto Cientifico Python Reproducible

## Conventions & Patterns
(Subagents append findings here after each task)


## 2026-02-11 - Task 1: DevContainer Setup

### Completed
- Created `.devcontainer/Dockerfile` with Python 3.11-slim base
  - Installs git, make, build-essential for scientific tooling
  - Upgrades pip/setuptools/wheel for modern Python packaging
  - Uses `/work` as generic workdir (mount-agnostic)
  
- Created `.devcontainer/devcontainer.json`
  - Configured VS Code extensions: Python, Pylance, Black, Ruff, Jupyter
  - Build context set to `..` (parent of .devcontainer/)
  - Container name: `science-python`

### Files Created
- `.devcontainer/Dockerfile` - 16 lines, follows plan specification exactly
- `.devcontainer/devcontainer.json` - Valid JSON, 19 lines

### Patterns Applied
- **Mirror-Environment Pattern**: DevContainer config will be mirrored in CI (Task 3)
- **Minimal Base Image**: python:3.11-slim reduces attack surface and build time
- **Layered RUN Commands**: Single RUN for apt-get to minimize Docker layers
- **No-install-recommends**: Reduces image size by ~100MB


## 2026-02-11 - Task 2: Python Package Structure with src-layout

**What worked:**
- Modern pyproject.toml with setuptools>=68 and src-layout works cleanly
- Package installed successfully with `pip install -e ".[dev]"`
- Import resolves to src/ directory as expected: `/path/to/src/science_lib/__init__.py`
- app/main.py successfully imports and uses science_lib.core
- pytest passes with single test

**Important gotcha discovered:**
- Creating `tests/science_lib/__init__.py` causes namespace shadowing
- This shadows the installed package and causes `ModuleNotFoundError` in pytest
- Solution: Remove `__init__.py` from test subdirectories that mirror package names
- Test files can import from installed package without local __init__.py

**Pattern to follow:**
```
tests/
  conftest.py
  science_lib/          # No __init__.py here!
    test_core.py        # Can import from science_lib package
```

**Verification commands all passed:**
1. `pip install -e ".[dev]"` - exit 0
2. Import check shows src/ path - exit 0  
3. `python app/main.py` outputs "Result: 5" - exit 0
4. `pytest -q` passes 1 test - exit 0

**Dependencies installed:**
- pytest 9.0.2 (upgraded from 7.4.4)
- sphinx 7+ (already present)
- sphinx-rtd-theme 3.1.0
- pluggy 1.6.0 (upgraded from 1.0.0)

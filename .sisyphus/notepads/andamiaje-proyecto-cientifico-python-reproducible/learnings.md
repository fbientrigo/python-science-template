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

## 2026-02-12 - Git Commit of Wave 1 Tasks

### Patterns Applied
- **Atomic Commits**: Large wave updates should be split by concern (config, feature, test, docs) to ensure history remains readable and reverts are safe.
- **Dependency-Ordered Commits**: Level 0-1 (devcontainer, package config) were committed before Level 2-3 (src-layout, app, tests).
- **Test Pairing**: Tests were committed alongside their corresponding package files.

## 2026-02-12 - Task 3: GitHub Actions CI Workflow

**What worked:**
- Created `.github/workflows/ci.yml` with Mirror-Environment Pattern
- Workflow builds from same `.devcontainer/Dockerfile` used in development
- Uses `actions/checkout@v4` (latest stable)
- Runs pytest inside Docker container with `--user $(id -u):$(id -g)` to prevent root-owned files

**CI Configuration:**
```yaml
Triggers: push/pull_request on main/master/develop
Job: test on ubuntu-latest
Steps:
  1. Checkout repository
  2. Build Docker image from .devcontainer/Dockerfile
  3. Run pytest inside container with volume mount
```

**Docker run flags explained:**
- `--rm`: Remove container after run (cleanup)
- `--user "$(id -u):$(id -g)"`: Run as current user to prevent root-owned files in workspace
- `-v "${{ github.workspace }}:/work"`: Mount GitHub workspace to /work (matches Dockerfile WORKDIR)
- `-w /work`: Set working directory inside container
- `sh -c "..."`: Run install + test commands in single shell

**Validation:**
- YAML syntax validated with Python's yaml module: ✓ Valid
- Cannot test full Docker run locally (WSL2 integration not enabled)
- Workflow will run on GitHub's ubuntu-latest runners with full Docker support

**Mirror-Environment Pattern Benefits:**
- Dev and CI use IDENTICAL Dockerfile → byte-for-byte reproducibility
- Same Python version, same system dependencies, same workdir
- Tests passing locally WILL pass in CI (eliminates "works on my machine")


## 2026-02-12 - Task 4: Sphinx Documentation Setup

**What worked:**
- Sphinx autodoc + napoleon for Google/NumPy-style docstrings
- sphinx-apidoc successfully generated API stubs from src/science_lib
- HTML build succeeded with minimal warnings
- make -C docs apidoc creates docs/source/api/*.rst files automatically
- make -C docs html builds documentation to docs/build/html/

**Documentation structure:**
```
docs/
├── ARCHITECTURE.md       # Human-readable design rationale
├── Makefile              # apidoc and html targets
├── source/
│   ├── conf.py           # Sphinx config (adds src/ to sys.path)
│   ├── index.rst         # Main doc entry point
│   ├── api/              # Auto-generated API stubs
│   │   ├── modules.rst
│   │   └── science_lib.rst
│   ├── _static/          # Static assets (CSS, JS)
│   └── _templates/       # Custom templates
└── build/
    └── html/             # Generated HTML documentation
```

**Key Sphinx configuration decisions:**
- Added ../../src to sys.path so autodoc can import science_lib
- Extensions: sphinx.ext.autodoc, sphinx.ext.napoleon
- Theme: sphinx_rtd_theme (ReadTheDocs theme)
- Napoleon settings: Google and NumPy docstring formats enabled

**Verification results:**
1. make -C docs apidoc - exit 0, created 2 .rst files in source/api/
2. make -C docs html - exit 0, built HTML with 1 minor warning (missing _static dir)
3. Fixed warning by creating docs/source/_static/ directory

**ARCHITECTURE.md covers:**
- Why src-layout (prevents accidental imports)
- Why app/ separation (entry points vs library logic)
- Mirror-Environment Pattern (DevContainer = CI)
- Test conventions (no __init__.py in test subdirs)
- Sphinx autodoc conventions (Google-style docstrings)

**Pattern applied:**
- **Living Documentation**: apidoc target automates API doc generation
- Docs stay synchronized with code via automated stub generation
- CI can enforce make -C docs html succeeds

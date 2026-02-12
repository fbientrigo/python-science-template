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

## 2026-02-12 - Task 3: CI Workflow Architecture Decisions

### D5: Mirror-Environment Pattern
**Decision**: Build CI from `.devcontainer/Dockerfile` instead of using pre-built GitHub Actions
**Rationale**:
- Guarantees dev/CI environment parity (same base image, dependencies, Python version)
- Eliminates "works in my devcontainer but not in CI" issues
- Single source of truth for environment configuration
- Aligns with scientific reproducibility principles

### D6: Docker --user Flag
**Decision**: Run container with `--user "$(id -u):$(id -g)"` instead of default root
**Rationale**:
- Prevents pytest from creating cache files owned by root
- GitHub Actions workspace must be writable by runner user
- Matches devcontainer behavior (non-root user)
- Avoids permission errors on subsequent CI runs

### D7: Trigger Branches
**Decision**: Trigger on main/master/develop (not all branches)
**Rationale**:
- Reduces CI minutes for experimental feature branches
- Developers can still run tests locally in devcontainer
- Pull requests to these branches will still trigger CI
- Can be expanded later if needed

### D8: Single Job Architecture
**Decision**: One job "test" instead of matrix (multi-version, multi-OS)
**Rationale**:
- Project uses pinned Python 3.11 in devcontainer
- Scientific reproducibility requires FIXED environment, not compatibility testing
- Can add matrix later if cross-version support becomes requirement
- Keeps CI fast and focused

### D9: Install + Test in Container
**Decision**: Run `pip install -e '.[dev]'` inside container (not in Dockerfile)
**Rationale**:
- Dockerfile is reusable for any project (generic devcontainer)
- GitHub workspace is mounted at runtime → package install must happen then
- Mirrors local development workflow (devcontainer auto-installs via postCreateCommand)
- Keeps Dockerfile clean and project-agnostic


## 2026-02-12 - Task 4: Sphinx Documentation Decisions

### D10: Sphinx Theme Selection
**Decision**: Use `sphinx_rtd_theme` (ReadTheDocs theme)
**Rationale**:
- Professional appearance, widely recognized in Python community
- Mobile-responsive design
- Built-in search functionality
- Better navigation for large projects
- Already installed as dev dependency

### D11: Docstring Format
**Decision**: Support both Google and NumPy-style docstrings via Napoleon
**Rationale**:
- Google style: More readable, common in industry
- NumPy style: Standard in scientific Python libraries
- Napoleon extension parses both into reStructuredText
- Flexibility for contributors with different backgrounds

### D12: Makefile Targets
**Decision**: Separate `apidoc` and `html` targets instead of combined
**Rationale**:
- Allows developers to regenerate API stubs without full rebuild
- CI can run both targets sequentially for validation
- `apidoc` can be run before committing to ensure stubs are updated
- More granular control over documentation workflow

### D13: ARCHITECTURE.md Location
**Decision**: Place in `docs/` directory, not project root
**Rationale**:
- Groups all documentation in one location
- Keeps project root clean
- Can be symlinked or referenced from README if needed
- Follows convention of many scientific Python projects

### D14: sys.path Configuration
**Decision**: Add `../../src` to sys.path in conf.py instead of installing package
**Rationale**:
- Sphinx autodoc needs to import modules to extract docstrings
- Adding to sys.path allows autodoc to find `science_lib` package
- Works in CI without separate pip install step
- Simpler for read-the-docs integration later


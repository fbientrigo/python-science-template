# Architecture Documentation

This document explains the design decisions and patterns used in this scientific Python project.

## Table of Contents

1. [Package Structure: src-layout](#package-structure-src-layout)
2. [Application vs Library Separation](#application-vs-library-separation)
3. [Reproducibility Guarantee](#reproducibility-guarantee)
4. [Test Conventions](#test-conventions)
5. [Documentation Conventions](#documentation-conventions)

---

## Package Structure: src-layout

### Why src-layout?

This project uses the **src-layout** pattern instead of a flat layout:

```
project/
├── src/
│   └── science_lib/    # Package code here
│       ├── __init__.py
│       └── core.py
└── tests/
    └── science_lib/    # Tests mirror src/ structure
        └── test_core.py
```

**Benefits:**

1. **Prevents accidental imports**: During development, Python cannot import from the local `src/` directory unless the package is properly installed. This catches packaging issues early.

2. **Forces testing against installed package**: When you run `pytest`, it imports from the installed package (via `pip install -e .`), not from local files. This ensures your tests validate the actual distribution.

3. **Industry best practice**: Recommended by PyPA (Python Packaging Authority) for modern Python projects.

**Gotcha:** Never add `__init__.py` to test subdirectories that mirror package names (e.g., `tests/science_lib/__init__.py`). This causes namespace shadowing and breaks imports.

---

## Application vs Library Separation

### Directory Structure

```
project/
├── src/
│   └── science_lib/    # Reusable library code
│       ├── core.py
│       └── utils.py
└── app/
    └── main.py         # Entry points / CLI scripts
```

### Why separate app/ from src/?

- **`src/science_lib/`**: Contains pure library logic that can be imported and tested in isolation. This code should have minimal side effects and be highly reusable.

- **`app/`**: Contains entry points, CLI scripts, and orchestration code that ties together library components. This is where `if __name__ == "__main__"` blocks live.

**Benefits:**
- Clean separation of concerns
- Library can be imported without executing entry points
- Easier to test library logic independently
- Supports multiple entry points (CLI, web API, notebooks) using same library

---

## Reproducibility Guarantee

### Mirror-Environment Pattern

This project uses the **Mirror-Environment Pattern**: Your development environment (DevContainer) is byte-for-byte identical to your testing environment (CI).

```
┌─────────────────────┐      ┌─────────────────────┐
│  DevContainer       │      │  GitHub Actions CI  │
│                     │      │                     │
│  FROM python:3.11   │ ───▶ │  FROM python:3.11   │
│  RUN apt-get...     │ SAME │  RUN apt-get...     │
│  RUN pip install... │      │  RUN pip install... │
└─────────────────────┘      └─────────────────────┘
```

**Implementation:**
- `.devcontainer/Dockerfile` defines the exact environment
- CI workflow uses **identical** Dockerfile for testing
- No "works on my machine" issues

**Benefits:**
1. **Scientific reproducibility**: Results are identical across machines
2. **Zero environment drift**: Dev and CI cannot diverge
3. **Fast onboarding**: New contributors get correct environment instantly
4. **Audit trail**: Dockerfile serves as executable documentation of dependencies

### Base Image: python:3.11-slim

- **Why Slim?**: Debian-based (better compatibility than Alpine), includes glibc (required by NumPy/SciPy), smaller than full image (~150MB vs ~1GB)
- **Why Python 3.11?**: Modern Python with performance improvements, stable for scientific libraries

---

## Test Conventions

### Directory Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
└── science_lib/          # NO __init__.py here!
    └── test_core.py      # Tests for src/science_lib/core.py
```

### Rules

1. **Mirror src/ structure**: Test directories should mirror the package structure for discoverability.

2. **No `__init__.py` in test subdirs**: NEVER create `tests/science_lib/__init__.py`. This causes namespace shadowing and prevents pytest from importing the installed package.

3. **Import from installed package**: Tests should import via:
   ```python
   from science_lib.core import add_numbers  # Correct
   ```
   Not via relative imports or sys.path hacks.

4. **Run tests against installed package**: Always run `pip install -e ".[dev]"` before `pytest`. This ensures you're testing the distribution, not local files.

### Example Test

```python
# tests/science_lib/test_core.py
from science_lib.core import add_numbers

def test_add_numbers():
    """Test basic addition."""
    assert add_numbers(2, 3) == 5
```

---

## Documentation Conventions

### Sphinx + autodoc + napoleon

This project uses **Sphinx** with two key extensions:

1. **`sphinx.ext.autodoc`**: Automatically generates API documentation from docstrings in source code.

2. **`sphinx.ext.napoleon`**: Parses Google-style and NumPy-style docstrings into reStructuredText.

### Docstring Style: Google Format

```python
def add_numbers(a, b):
    """Add two numbers together.

    This is a simple addition function that demonstrates
    proper docstring formatting for Sphinx autodoc.

    Args:
        a: First number (int or float)
        b: Second number (int or float)

    Returns:
        Sum of a and b

    Raises:
        TypeError: If inputs are not numeric

    Example:
        >>> add_numbers(2, 3)
        5
    """
    return a + b
```

### Building Documentation

```bash
# Generate API stubs from source code
make -C docs apidoc

# Build HTML documentation
make -C docs html

# View docs: open docs/build/html/index.html
```

### Configuration

- **Sphinx config**: `docs/source/conf.py`
  - Adds `src/` to `sys.path` so autodoc can import `science_lib`
  - Configures extensions and theme (sphinx_rtd_theme)

- **Makefile**: `docs/Makefile`
  - `apidoc` target: Runs `sphinx-apidoc` to generate `.rst` stubs
  - `html` target: Builds HTML documentation
  - `clean` target: Removes build artifacts

### Living Documentation

The `apidoc` target ensures documentation stays synchronized with code:

1. Developer updates docstrings in `src/science_lib/`
2. `make -C docs apidoc` regenerates `.rst` stubs
3. `make -C docs html` rebuilds HTML with latest changes
4. CI can enforce documentation builds successfully

**Result:** Documentation is always up-to-date with the codebase.

---

## Summary

This project follows modern Python best practices:

- ✅ **src-layout** prevents import issues and forces proper testing
- ✅ **app/ separation** keeps entry points distinct from library logic
- ✅ **Mirror-Environment Pattern** guarantees reproducibility
- ✅ **Proper test conventions** ensure tests validate the installed package
- ✅ **Sphinx autodoc** keeps documentation synchronized with code

For questions or issues, refer to individual section details above.

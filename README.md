# python-science-template

This project follows the Mirror-Environment Pattern: your development environment (DevContainer) matches your testing environment (GitHub Actions) by running verification inside the same Docker image.

## Quickstart (Docker verification)

The project uses a **Clean Verification Flow** to ensure reproducibility and avoid polluting the host workspace with root-owned artifacts (like `__pycache__` or `.pytest_cache`).

### 1. Build the image

```bash
make docker-build
```

### 2. Run verification

The standard verification target mounts your source code as **read-only** and performs the installation and testing inside a temporary directory in the container:

```bash
make docker-verify
```

This command:
- Mounts the current directory as `:ro`.
- Copies the source to `/tmp/work` to avoid permission issues during installation.
- Creates a virtual environment in `/tmp/venv`.
- Installs the package with `[test]` extras.
- Runs tests and the entrypoint.

### Dependency Extras
- `pip install '.[test]'`: Minimal dependencies for running tests (used in CI).
- `pip install '.[dev]'`: Full development environment, including documentation tools (Sphinx) and testing utilities.

## Troubleshooting

### Persistence of root-owned files
If you previously ran commands that created files inside the container with a read-write mount, they might be owned by `root` on your host. Use this to clean them:

```bash
make clean
```

### Failures in Read-Only mode
Some legacy Python packaging tools might try to write to the source directory even during installation (e.g., updating `src/*.egg-info`). 

If `make docker-verify` fails due to read-only restrictions, you can use the debug target which uses a read-write mount:

```bash
make docker-verify-rw
```
*Note: This may create root-owned artifacts in your workspace.*

CI runs the same `make docker-verify` step.

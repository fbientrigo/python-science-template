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

## Design Rationale: Permission & CI Hardening

This template is designed to be "CI-native" by avoiding common pitfalls with Docker permissions and volume mounts.

### Why we avoid `docker run --user $(id -u):$(id -g)`
While mapping the host UID/GID to the container is a common local development pattern, we avoid it in CI for several reasons:
1.  **Identity Mismatch**: In environments like GitHub Actions, the runner UID (typically 1001) may not exist in the container's `/etc/passwd`, leading to "I have no name!" errors and broken tool behavior.
2.  **Home Directory Access**: Many tools (pip, git, etc.) expect a valid `$HOME`. If you force a UID that doesn't have a home directory defined in the image, these tools may fail or try to write to `/`, which is restricted.
3.  **Portability**: The template should work regardless of the host's UID. By running as the container's internal user (`app`) and isolating all write operations to `/tmp`, we ensure consistent behavior across local and CI environments.

### Hardening with `HOME=/tmp` and `PYTHONNOUSERSITE=1`
To make the container execution truly ephemeral and secure:
-   **`HOME=/tmp`**: We override the home directory to `/tmp`. Since `/tmp` is world-writable, this guarantees that any tool attempting to write configuration or cache to `~` will succeed without needing complex volume permission management.
-   **`PYTHONNOUSERSITE=1`**: This prevents Python from loading packages from the user-specific site-packages directory (usually `~/.local`). This ensures that the environment is strictly defined by the virtual environment created during verification, preventing "poisoning" from the container's global state.

### Debugging non-root containers
If you need to use a different non-root user or if you encounter permission issues:
1.  Use `make docker-verify-rw` to run with a read-write mount and inspect the artifacts.
2.  Verify that your container user has write access to `/tmp`.
3.  Check if your source code contains pre-existing `*.egg-info` or `__pycache__` directories owned by `root`, which might interfere with the `cp -a` command or tool execution.

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

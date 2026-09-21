# Scientific Python Template

A small project template for researchers who want **one reproducible verification path** instead of separate local and CI environments.

The same Dockerfile powers the Dev Container and `make verify`; GitHub Actions runs that same command. Verification mounts your checkout read-only, copies it into an ephemeral container workspace, then installs, lints, tests, builds docs, and runs a smoke entry point.

## 30-second start

1. Click **Use this template** on GitHub and clone the new repository.
2. Initialize it:

```bash
python scripts/init_project.py
```

3. Verify exactly what CI will verify:

```bash
make verify
```

For non-interactive setup:

```bash
python scripts/init_project.py \
  --name my-analysis \
  --description "Muon-background analysis" \
  --author "Your Name" \
  --profile eda
```

### Project profiles

The initializer asks one practical question: **what kind of scientific project is this?** It then adds only a minimal proof-of-life harness.

| Profile | Adds | Proof of life |
| --- | --- | --- |
| `generic` | standard library only | summarize a numeric sample |
| `eda` | pandas | summarize numeric columns in a DataFrame |
| `ml` | scikit-learn | fit and predict with a deterministic baseline |
| `api` | FastAPI + Uvicorn | create an app with `/health` |

These are starting harnesses, not frameworks. Delete or replace them once your real project has equivalent coverage.

<!-- TEMPLATE-ONLY:START -->
## Why this template exists

Scientific projects often drift into three subtly different environments: a laptop, a container, and CI. This template deliberately rejects that split.

```text
source checkout (read-only)
          │
          ▼
.devcontainer/Dockerfile
          │
    ┌─────┴─────┐
    ▼           ▼
Dev Container   make verify / GitHub Actions
                │
                ▼
        ephemeral /tmp/work
                │
          uv sync --frozen
                │
       lint + tests + docs + smoke
```

The initializer creates a `uv.lock` for the selected profile when `uv` can reach the package index. The template itself stays profile-neutral.
<!-- TEMPLATE-ONLY:END -->

## Fast local iteration

If you do not need the full container gate on every edit:

```bash
uv sync --group dev --group docs --frozen
make local-verify
```

`make local-verify` runs the same lint/test/docs/smoke checks in your current environment. `make verify` remains the canonical gate.

## What is intentionally not included

No notebook framework, experiment tracker, cloud stack, database, LLM integration, or deployment platform is selected for you. Add those only when the project actually needs them.

## Reproducibility contract

- `scripts/init_project.py` creates `uv.lock` after profile selection; when present, every verification uses it with `--frozen`.
- `.devcontainer/Dockerfile` defines the OS/Python toolchain used by development and verification.
- Before initialization, or if a lockfile is intentionally absent, the commands emit a warning and resolve from `pyproject.toml` instead of pretending the environment is frozen.
- `make verify` mounts the repository read-only and performs writes only in an ephemeral copy.
- CI calls `make verify`; it does not reimplement installation or testing separately.
- `make local-verify` is a convenience path, not the canonical reproducibility proof.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the design rationale.

## License

MIT.

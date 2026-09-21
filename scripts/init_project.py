"""Initialize a repository created from python-science-template.

The script intentionally does only four things: rename metadata/package paths,
select one small project profile, write a proof-of-life harness, and refresh the
uv lockfile when uv is available.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_MODULE = "science_project"
BASE_DIST = "science-project"
BASE_TITLE = "Science Project"
BASE_AUTHOR = "Science Team"
SCAFFOLD_VERSION = "0.2.0"

TEXT_SUFFIXES = {".py", ".toml", ".md", ".rst", ".yml", ".yaml", ".json", ".txt"}
SKIP_DIRS = {".git", ".venv", "docs/build", "__pycache__"}


@dataclass(frozen=True)
class Profile:
    dependencies: tuple[str, ...]
    harness_filename: str
    harness: str
    test_filename: str
    test: str
    app: str
    run_hint: str


def profile_spec() -> dict[str, Profile]:
    return {
        "generic": Profile(
            dependencies=(),
            harness_filename="harness.py",
            harness="""\
# Small generic harness that should be replaced by real project logic.

from statistics import fmean


def summarize(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("values must not be empty")
    return {
        "count": len(values),
        "mean": fmean(values),
        "minimum": min(values),
        "maximum": max(values),
    }
""",
            test_filename="test_harness.py",
            test="""\
from __MODULE__.harness import summarize


def test_summarize_numeric_sample() -> None:
    assert summarize([1.0, 2.0, 3.0])["mean"] == 2.0
""",
            app="""\
import json

from __MODULE__.harness import summarize


if __name__ == "__main__":
    print(json.dumps(summarize([1.0, 2.0, 3.0]), sort_keys=True))
""",
            run_hint="uv run python app/main.py",
        ),
        "eda": Profile(
            dependencies=("pandas>=2.2",),
            harness_filename="analysis.py",
            harness="""\
# Minimal tabular EDA harness.

import pandas as pd


def summarize_numeric(frame: pd.DataFrame) -> pd.DataFrame:
    # Return a compact summary of numeric columns.
    numeric = frame.select_dtypes(include="number")
    if numeric.shape[1] == 0:
        raise ValueError("frame has no numeric columns")
    return numeric.describe().T[["count", "mean", "std", "min", "max"]]
""",
            test_filename="test_analysis.py",
            test="""\
import pandas as pd

from __MODULE__.analysis import summarize_numeric


def test_summarize_numeric() -> None:
    frame = pd.DataFrame({"x": [1.0, 2.0, 3.0], "label": ["a", "b", "c"]})
    summary = summarize_numeric(frame)
    assert summary.loc["x", "mean"] == 2.0
    assert list(summary.index) == ["x"]
""",
            app="""\
import pandas as pd

from __MODULE__.analysis import summarize_numeric


if __name__ == "__main__":
    demo = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 2.0, 1.0]})
    print(summarize_numeric(demo).to_string())
""",
            run_hint="uv run python app/main.py",
        ),
        "ml": Profile(
            dependencies=("scikit-learn>=1.5",),
            harness_filename="model.py",
            harness="""\
# Minimal deterministic ML baseline.

from collections.abc import Sequence

from sklearn.linear_model import LogisticRegression


def fit_baseline(
    features: Sequence[Sequence[float]], labels: Sequence[int]
) -> LogisticRegression:
    # Fit a tiny deterministic classifier as a pipeline smoke test.
    model = LogisticRegression(random_state=0, solver="liblinear")
    return model.fit(features, labels)
""",
            test_filename="test_model.py",
            test="""\
from __MODULE__.model import fit_baseline


def test_fit_baseline_predicts_training_sample() -> None:
    x = [[0.0], [0.2], [0.8], [1.0]]
    y = [0, 0, 1, 1]
    model = fit_baseline(x, y)
    assert model.predict([[0.1], [0.9]]).tolist() == [0, 1]
""",
            app="""\
from __MODULE__.model import fit_baseline


if __name__ == "__main__":
    x = [[0.0], [0.2], [0.8], [1.0]]
    y = [0, 0, 1, 1]
    model = fit_baseline(x, y)
    print(model.predict([[0.1], [0.9]]).tolist())
""",
            run_hint="uv run python app/main.py",
        ),
        "api": Profile(
            dependencies=("fastapi>=0.115", "uvicorn>=0.30"),
            harness_filename="api.py",
            harness="""\
# Minimal FastAPI application.

from fastapi import FastAPI

app = FastAPI(title="__TITLE__")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
""",
            test_filename="test_api.py",
            test="""\
from __MODULE__.api import app, health


def test_health_contract() -> None:
    assert health() == {"status": "ok"}
    assert "/health" in {route.path for route in app.routes}
""",
            app="""\
from __MODULE__.api import app


if __name__ == "__main__":
    paths = sorted(route.path for route in app.routes if hasattr(route, "path"))
    print(f"API ready with routes: {paths}")
    print("Run: uv run uvicorn __MODULE__.api:app --reload")
""",
            run_hint="uv run uvicorn __MODULE__.api:app --reload",
        ),
    }


def _ascii_slug_source(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    return normalized.encode("ascii", "ignore").decode("ascii")


def module_name_from_project(name: str) -> str:
    source = _ascii_slug_source(name)
    module = re.sub(r"[^a-zA-Z0-9]+", "_", source.strip()).strip("_").lower()
    if not module:
        raise ValueError("project name must contain letters or numbers")
    if module[0].isdigit():
        module = f"project_{module}"
    if not module.isidentifier():
        raise ValueError(f"cannot derive a valid Python module from {name!r}")
    return module


def distribution_name(name: str) -> str:
    source = _ascii_slug_source(name)
    dist = re.sub(r"[^a-zA-Z0-9]+", "-", source.strip()).strip("-").lower()
    if not dist:
        raise ValueError("project name must contain letters or numbers")
    return dist


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name")
    parser.add_argument("--module")
    parser.add_argument("--description")
    parser.add_argument("--author")
    parser.add_argument("--profile", choices=tuple(profile_spec()))
    parser.add_argument("--no-lock", action="store_true", help="do not run `uv lock`")
    parser.add_argument("--yes", action="store_true", help="accept defaults without prompting")
    return parser.parse_args()


def prompt(value: str | None, label: str, default: str, *, noninteractive: bool) -> str:
    if value:
        return value.strip()
    if noninteractive:
        return default
    entered = input(f"{label} [{default}]: ").strip()
    return entered or default


def replace_text(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(root).as_posix()
        if any(relative == skip or relative.startswith(f"{skip}/") for skip in SKIP_DIRS):
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in replacements.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def set_project_dependencies(pyproject: Path, dependencies: tuple[str, ...]) -> None:
    text = pyproject.read_text(encoding="utf-8")
    rendered = "dependencies = [" + ", ".join(json.dumps(dep) for dep in dependencies) + "]"
    text, count = re.subn(r"(?m)^dependencies = \[[^\n]*\]$", rendered, text, count=1)
    if count != 1:
        raise RuntimeError("expected exactly one single-line project dependencies entry")
    pyproject.write_text(text, encoding="utf-8")


def set_template_state(pyproject: Path, profile: str, initialized: bool) -> None:
    text = pyproject.read_text(encoding="utf-8")
    text = re.sub(r'(?m)^profile = ".*"$', f'profile = "{profile}"', text, count=1)
    text = re.sub(
        r"(?m)^initialized = (true|false)$",
        f"initialized = {'true' if initialized else 'false'}",
        text,
        count=1,
    )
    pyproject.write_text(text, encoding="utf-8")


def replace_template_readme_section(readme: Path, profile: str, run_hint: str) -> None:
    text = readme.read_text(encoding="utf-8")
    block = f"""\
## Project setup

This repository was initialized from `fbientrigo/python-science-template`
with the **{profile}** profile.

```bash
uv sync --group dev --group docs
uv lock
make verify
```

Profile smoke command:

```bash
{run_hint}
```

The starter harness is intentionally small. Replace it with real project logic
while keeping at least one fast proof-of-life test.
"""
    text, count = re.subn(
        r"<!-- TEMPLATE-ONLY:START -->.*?<!-- TEMPLATE-ONLY:END -->",
        block.rstrip(),
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("template README markers are missing or duplicated")
    readme.write_text(text, encoding="utf-8")


def regenerate_lock(root: Path) -> bool:
    lock = root / "uv.lock"
    lock.unlink(missing_ok=True)
    uv = shutil.which("uv")
    if uv is None:
        print("NOTE: uv is not installed; run `uv lock` before `make verify`.", file=sys.stderr)
        return False
    result = subprocess.run([uv, "lock"], cwd=root, check=False)
    if result.returncode != 0:
        lock.unlink(missing_ok=True)
        print(
            "NOTE: `uv lock` failed; initialization succeeded but verification needs a lockfile.",
            file=sys.stderr,
        )
        return False
    return True


def main() -> int:
    args = parse_args()
    pyproject = ROOT / "pyproject.toml"
    current = pyproject.read_text(encoding="utf-8")
    if "initialized = true" in current:
        raise SystemExit("This repository has already been initialized.")

    name = prompt(args.name, "Project name", BASE_TITLE, noninteractive=args.yes)
    dist = distribution_name(name)
    module = args.module or module_name_from_project(name)
    if not module.isidentifier():
        raise SystemExit(f"Invalid module name: {module!r}")
    description = prompt(
        args.description,
        "Description",
        "Reproducible scientific Python project",
        noninteractive=args.yes,
    )
    author = prompt(args.author, "Author", BASE_AUTHOR, noninteractive=args.yes)
    profile = prompt(
        args.profile,
        "Profile (generic/eda/ml/api)",
        "generic",
        noninteractive=args.yes,
    )
    specs = profile_spec()
    if profile not in specs:
        raise SystemExit(f"Unknown profile {profile!r}; choose one of: {', '.join(specs)}")
    spec = specs[profile]

    src_old = ROOT / "src" / BASE_MODULE
    src_new = ROOT / "src" / module
    tests_old = ROOT / "tests" / BASE_MODULE
    tests_new = ROOT / "tests" / module
    if src_new != src_old:
        src_old.rename(src_new)
    if tests_new != tests_old:
        tests_old.rename(tests_new)

    replacements = {
        BASE_DIST: dist,
        BASE_MODULE: module,
        BASE_TITLE: name,
        BASE_AUTHOR: author,
        'description = "Reproducible scientific Python project"': (
            f'description = {json.dumps(description)}'
        ),
    }
    replace_text(ROOT, replacements)
    set_project_dependencies(pyproject, spec.dependencies)
    set_template_state(pyproject, profile, True)

    # Replace the generic harness with the selected profile's small proof of life.
    for candidate in src_new.glob("*.py"):
        if candidate.name != "__init__.py":
            candidate.unlink()
    for candidate in tests_new.glob("test_*.py"):
        candidate.unlink()

    def render(text: str) -> str:
        return text.replace("__MODULE__", module).replace("__TITLE__", name)

    (src_new / spec.harness_filename).write_text(render(spec.harness), encoding="utf-8")
    (tests_new / spec.test_filename).write_text(render(spec.test), encoding="utf-8")
    (ROOT / "app" / "main.py").write_text(render(spec.app), encoding="utf-8")

    export = {
        "generic": "summarize",
        "eda": "summarize_numeric",
        "ml": "fit_baseline",
        "api": "app",
    }[profile]
    module_stem = Path(spec.harness_filename).stem
    (src_new / "__init__.py").write_text(
        (
            f'"""{name} package."""\n\n'
            f"from {module}.{module_stem} import {export}\n\n"
            f'__all__ = ["{export}"]\n'
        ),
        encoding="utf-8",
    )

    replace_template_readme_section(ROOT / "README.md", profile, render(spec.run_hint))
    # Template-only tests should not leak into generated research projects.
    (ROOT / "tests" / "test_initializer.py").unlink(missing_ok=True)

    (ROOT / ".science-template.json").write_text(
        json.dumps(
            {
                "scaffold_version": SCAFFOLD_VERSION,
                "distribution": dist,
                "module": module,
                "profile": profile,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    lock_ok = True if args.no_lock else regenerate_lock(ROOT)
    print(f"Initialized {name!r} as module {module!r} with profile {profile!r}.")
    if args.no_lock:
        print("Skipped lock generation; run `uv lock` before `make verify`.")
    elif lock_ok:
        print("Updated uv.lock.")
    print("Next: make verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

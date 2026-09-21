import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
with (ROOT / "pyproject.toml").open("rb") as handle:
    pyproject = tomllib.load(handle)

project = pyproject["tool"]["science-template"]["project_title"]
author = pyproject["project"]["authors"][0]["name"]
release = pyproject["project"]["version"]

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
exclude_patterns: list[str] = []
html_theme = "sphinx_rtd_theme"
napoleon_numpy_docstring = True

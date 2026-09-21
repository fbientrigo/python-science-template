import runpy
from pathlib import Path

INITIALIZER = runpy.run_path("scripts/init_project.py")
module_name_from_project = INITIALIZER["module_name_from_project"]
profile_spec = INITIALIZER["profile_spec"]


def test_module_name_from_project() -> None:
    assert module_name_from_project("Muon Background 2026") == "muon_background_2026"
    assert module_name_from_project("3D-analysis") == "project_3d_analysis"


def test_profiles_are_small_and_explicit() -> None:
    assert set(profile_spec()) == {"generic", "eda", "ml", "api"}
    for spec in profile_spec().values():
        assert len(spec.dependencies) <= 2
        assert spec.harness_filename.endswith(".py")


def test_template_metadata_exists() -> None:
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.science-template]" in text
    assert "initialized = false" in text

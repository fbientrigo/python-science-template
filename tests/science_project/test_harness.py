from science_project.harness import summarize


def test_summarize_numeric_sample() -> None:
    result = summarize([1.0, 2.0, 3.0])
    assert result == {"count": 3, "mean": 2.0, "minimum": 1.0, "maximum": 3.0}

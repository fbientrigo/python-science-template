# Small generic harness that should be replaced by real project logic.

from statistics import fmean


def summarize(values: list[float]) -> dict[str, float | int]:
    """Return a tiny deterministic summary for a numeric sample."""
    if not values:
        raise ValueError("values must not be empty")
    return {
        "count": len(values),
        "mean": fmean(values),
        "minimum": min(values),
        "maximum": max(values),
    }

"""
utils/ — UI helpers package.

This package re-exports everything from the original ``utils.py`` module so
any ``import utils`` in existing code (e.g. ``app.py``) continues to work
unchanged.  The ``highlights`` sub-module adds the enhanced
``generate_highlights()`` helper used by ``demo_pipeline.py``.
"""
from __future__ import annotations

from typing import Iterable, List

from models import SourceCoord

# ── Colour constants ──────────────────────────────────────────────────────
HIGHLIGHT_YELLOW = "rgba(255, 235, 100, 0.55)"
HIGHLIGHT_GREEN  = "rgba(170, 230, 170, 0.55)"
HIGHLIGHT_RED    = "rgba(255, 150, 150, 0.55)"


def highlight_coords(
    coords: Iterable[SourceCoord],
    color: str = HIGHLIGHT_YELLOW,
) -> List[dict]:
    """Convert pydantic ``SourceCoord``s into streamlit-pdf-viewer annotations."""
    out: List[dict] = []
    for c in coords or []:
        out.append({
            "page":    int(c.page),
            "x":       float(c.x),
            "y":       float(c.y),
            "width":   float(c.width),
            "height":  float(c.height),
            "color":   color,
            "tooltip": c.note or "Source",
        })
    return out


def confidence_color(score: int) -> str:
    """Green / amber / red traffic-light string for a confidence score."""
    if score >= 90:
        return "#1e6f31"
    if score >= 70:
        return "#b76e00"
    return "#a41818"


def confidence_badge(score: int) -> str:
    """HTML pill for inline display next to a field label."""
    cls = "badge-high" if score >= 90 else ("badge-med" if score >= 70 else "badge-low")
    return f'<span class="badge {cls}">{int(score)}%</span>'


def first_page(coords: Iterable[SourceCoord]) -> int:
    """Return the lowest page index across a set of coords; 0 if empty."""
    pages = [int(c.page) for c in coords or []]
    return min(pages) if pages else 0


# ── Re-export from sub-module so `import utils; utils.generate_highlights` works
from .highlights import generate_highlights  # noqa: E402

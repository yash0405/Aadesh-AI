"""
UI helpers: PDF highlight overlay payloads + confidence badges.
"""
from __future__ import annotations

from typing import Iterable, List

from models import SourceCoord

# Yellow translucent for primary highlight, green for verified, red for low conf.
HIGHLIGHT_YELLOW = "rgba(255, 235, 100, 0.55)"
HIGHLIGHT_GREEN  = "rgba(170, 230, 170, 0.55)"
HIGHLIGHT_RED    = "rgba(255, 150, 150, 0.55)"


def highlight_coords(coords: Iterable[SourceCoord],
                     color: str = HIGHLIGHT_YELLOW) -> List[dict]:
    """Convert pydantic `SourceCoord`s into streamlit-pdf-viewer annotations."""
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
    """Green / yellow / red traffic light for an integer confidence score."""
    if score >= 90:
        return "#1e6f31"   # green
    if score >= 70:
        return "#b76e00"   # amber
    return "#a41818"       # red


def confidence_badge(score: int) -> str:
    """HTML pill for inline display next to a field label."""
    cls = "badge-high" if score >= 90 else ("badge-med" if score >= 70 else "badge-low")
    return f'<span class="badge {cls}">{int(score)}%</span>'


def first_page(coords: Iterable[SourceCoord]) -> int:
    """First (lowest) page index across a set of coords; 0 if empty."""
    pages = [int(c.page) for c in coords or []]
    return min(pages) if pages else 0

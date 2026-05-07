"""
utils/highlights.py — Enhanced PDF highlight generator.

Provides ``generate_highlights()``, a higher-level helper that accepts an
``ExtractionResult`` and an optional selected field name, and returns the
streamlit-pdf-viewer annotation list for the PDF panel in ``app.py``.
"""
from __future__ import annotations

from typing import List, Optional

from models import ExtractionResult, SourceCoord

# Colour palette matching the app theme
_YELLOW = "rgba(255, 235, 100, 0.55)"   # active field highlight
_GOLD   = "rgba(201, 161,  74, 0.18)"   # background (all fields, unselected)
_GREEN  = "rgba(170, 230, 170, 0.55)"   # verified field


def _coords_to_annotations(
    coords: List[SourceCoord],
    color: str,
    tooltip_prefix: str = "",
) -> List[dict]:
    return [
        {
            "page":    int(c.page),
            "x":       float(c.x),
            "y":       float(c.y),
            "width":   float(c.width),
            "height":  float(c.height),
            "color":   color,
            "tooltip": f"{tooltip_prefix}{c.note or 'Source'}".strip(),
        }
        for c in coords
    ]


def generate_highlights(
    result: ExtractionResult,
    selected_field: Optional[str] = None,
) -> List[dict]:
    """Build annotation list for ``streamlit-pdf-viewer``.

    Parameters
    ----------
    result:
        The ``ExtractionResult`` from the pipeline.
    selected_field:
        The ``JudgmentField.name`` the user clicked on (e.g. ``"case_title"``).
        When provided, that field is rendered in bright yellow; all other fields
        are rendered in a faint gold.  When ``None``, every field gets faint gold
        (the "all-fields overview" state).

    Returns
    -------
    List[dict]  annotation dicts accepted by ``streamlit-pdf-viewer``.
    """
    annotations: List[dict] = []
    coords_map = result.coords_map()

    for field_name, coords in coords_map.items():
        if not coords:
            continue
        if selected_field and field_name == selected_field:
            color   = _YELLOW
            prefix  = f"[{field_name}]  "
        else:
            color   = _GOLD
            prefix  = ""
        annotations.extend(_coords_to_annotations(coords, color, prefix))

    return annotations

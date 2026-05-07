"""
Pydantic schema for the judgment extraction pipeline.

A `JudgmentField` is one extracted attribute (e.g. case_title, key_directions)
with its confidence score and the PDF coordinates that back it up.  The set of
fields together form an `ExtractionResult`, which is the contract returned by
`pipeline.extract()` and consumed by the Streamlit UI.
"""
from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SourceCoord(BaseModel):
    """A single rectangular highlight region on a PDF page (0-indexed page)."""
    page: int = Field(..., ge=0, description="0-indexed PDF page number")
    x: float = Field(..., description="Left edge in PDF points")
    y: float = Field(..., description="Top edge in PDF points")
    width: float = Field(..., description="Box width in PDF points")
    height: float = Field(..., description="Box height in PDF points")
    note: Optional[str] = Field(None, description="Human-readable source hint")


class JudgmentField(BaseModel):
    """One extracted field with provenance."""
    name: str
    value: Any                                      # str | list[str] | int
    confidence: int = Field(..., ge=0, le=100)
    source_coords: List[SourceCoord] = Field(default_factory=list)
    is_inferred: bool = False


class ExtractionResult(BaseModel):
    """Top-level extraction payload returned by the pipeline."""
    fields: List[JudgmentField]
    action_plan: Optional[dict] = None   # populated by llm_planner in full pipeline

    # Convenience helpers ────────────────────────────────────────────────
    def get(self, name: str) -> Optional[JudgmentField]:
        for f in self.fields:
            if f.name == name:
                return f
        return None

    def value(self, name: str, default: Any = None) -> Any:
        f = self.get(name)
        return f.value if f is not None else default

    def confidence_map(self) -> dict[str, int]:
        return {f.name: f.confidence for f in self.fields}

    def coords_map(self) -> dict[str, List[SourceCoord]]:
        return {f.name: f.source_coords for f in self.fields}

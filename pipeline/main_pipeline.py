"""
Stage 4 / Orchestrator: pdf_path → validated ExtractionResult.

Runs the full 4-step pipeline and returns a Pydantic-validated
``ExtractionResult`` with the action plan attached.

Usage
-----
    from pipeline.main_pipeline import run_pipeline

    result = run_pipeline("SC-Judgement.pdf")
    print(result.action_plan["priority"])   # → "HIGH"
    print(result.confidence_map())
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from models import ExtractionResult, JudgmentField, SourceCoord

from .pdf_processor import extract_text
from .llm_extractor import extract_fields
from .llm_planner    import generate_action_plan


# ── Static source-coordinate registry ─────────────────────────────────────
# In production the LLM would return bounding boxes for every span it used.
# For the mock we maintain this registry keyed on the normalised field name.
_COORDS: dict[str, list[dict]] = {
    "case_title": [
        {"page": 0,  "x": 100, "y": 50,  "width": 400, "height": 50,
         "note": "Page 1, heading"},
    ],
    "court": [
        {"page": 0,  "x": 100, "y": 20,  "width": 400, "height": 30,
         "note": "Page 1, court name banner"},
    ],
    "judgment_date": [
        {"page": 58, "x": 50,  "y": 600, "width": 550, "height": 100,
         "note": "Page 59, signature block"},
    ],
    "case_number": [
        {"page": 0,  "x": 100, "y": 120, "width": 400, "height": 40,
         "note": "Page 1, case-number header"},
    ],
    "judgment_summary": [
        {"page": 57, "x": 50,  "y": 300, "width": 550, "height": 200,
         "note": "Pages 58-59, final operative paragraphs"},
    ],
    "key_directions": [
        {"page": 57, "x": 50,  "y": 300, "width": 550, "height": 150,
         "note": "Pages 58-59, paragraphs 40-41"},
        {"page": 58, "x": 50,  "y": 80,  "width": 550, "height": 200,
         "note": "Page 59, continuation of operative directions"},
    ],
    "responsible_authority": [
        {"page": 1,  "x": 50,  "y": 100, "width": 550, "height": 120,
         "note": "Pages 2-10, party listings"},
        {"page": 56, "x": 50,  "y": 400, "width": 550, "height": 120,
         "note": "Pages 57-58, operative authority references"},
    ],
    "appeal_timeline": [
        {"page": 58, "x": 50,  "y": 600, "width": 550, "height": 100,
         "note": "Inferred from judgment date on page 59"},
    ],
}


def _mk_coords(key: str) -> List[SourceCoord]:
    return [SourceCoord(**c) for c in _COORDS.get(key, [])]


def _build_result(fields_dict: dict, action_plan: dict) -> ExtractionResult:
    """Map the flat LLM output dict → Pydantic-validated ExtractionResult."""
    conf = fields_dict.get("_confidence", {})

    # Responsible authorities: split comma-separated string → list
    dept_raw = fields_dict.get("responsible_department", "")
    authorities = [a.strip() for a in dept_raw.split(",") if a.strip()]

    appeal_days = int(action_plan.get("deadline_days", 90))

    judgment_fields = [
        JudgmentField(
            name="case_title",
            value=fields_dict.get("case_title", ""),
            confidence=conf.get("case_title", 90),
            source_coords=_mk_coords("case_title"),
        ),
        JudgmentField(
            name="court",
            value=fields_dict.get("court", ""),
            confidence=conf.get("court", 90),
            source_coords=_mk_coords("court"),
        ),
        JudgmentField(
            name="judgment_date",
            # LLM may return "date" or "judgment_date"
            value=fields_dict.get("date", fields_dict.get("judgment_date", "")),
            confidence=conf.get("date", conf.get("judgment_date", 90)),
            source_coords=_mk_coords("judgment_date"),
        ),
        JudgmentField(
            name="case_number",
            value=fields_dict.get("case_number", ""),
            confidence=conf.get("case_number", 90),
            source_coords=_mk_coords("case_number"),
        ),
        JudgmentField(
            name="judgment_summary",
            value=fields_dict.get("summary", fields_dict.get("judgment_summary", "")),
            confidence=conf.get("summary", conf.get("judgment_summary", 90)),
            source_coords=_mk_coords("judgment_summary"),
        ),
        JudgmentField(
            name="key_directions",
            value=fields_dict.get(
                "key_directives", fields_dict.get("key_directions", [])
            ),
            confidence=conf.get(
                "key_directives", conf.get("key_directions", 90)
            ),
            source_coords=_mk_coords("key_directions"),
        ),
        JudgmentField(
            name="responsible_authority",
            value=authorities,
            confidence=conf.get(
                "responsible_department", conf.get("responsible_authority", 90)
            ),
            source_coords=_mk_coords("responsible_authority"),
        ),
        JudgmentField(
            name="appeal_timeline",
            value=appeal_days,
            confidence=conf.get("appeal_timeline", 70),
            is_inferred=True,
            source_coords=_mk_coords("appeal_timeline"),
        ),
    ]

    return ExtractionResult(fields=judgment_fields, action_plan=action_plan)


# ── Main entry point ───────────────────────────────────────────────────────

def run_pipeline(pdf_path: str | Path) -> ExtractionResult:
    """Full 4-step pipeline: PDF → Text → LLM Extract → LLM Plan → Pydantic.

    Parameters
    ----------
    pdf_path:
        Path to the judgment PDF (can be a non-existent path; the pipeline
        falls back to static data gracefully).

    Returns
    -------
    ExtractionResult  (Pydantic-validated, ``action_plan`` dict attached).
    """
    sep = "═" * 58
    print(f"\n{sep}")
    print("  🚀  Judgment AI Pipeline  —  starting")
    print(f"      PDF : {pdf_path}")
    print(sep)

    # Step 1 ── PDF → raw text
    print("\n  [1/4]  PDF → Raw Text         (pdf_processor)")
    raw_text = extract_text(str(pdf_path))

    # Step 2 ── text → structured field dict
    print("\n  [2/4]  Text → Fields JSON     (llm_extractor)")
    fields_dict = extract_fields(raw_text)

    # Step 3 ── fields → action plan
    print("\n  [3/4]  Fields → Action Plan   (llm_planner)")
    action_plan = generate_action_plan(fields_dict)

    # Step 4 ── assemble + Pydantic-validate
    print("\n  [4/4]  Pydantic validation + coord enrichment")
    result = _build_result(fields_dict, action_plan)

    print(f"\n{sep}")
    print("  ✅  Pipeline complete:  PDF → Text → LLM Extract → LLM Plan")
    print(f"      Fields extracted : {len(result.fields)}")
    print(f"      Action priority  : {action_plan['priority']}")
    print(f"      Appeal deadline  : {action_plan['deadline_date']}")
    print(f"{sep}\n")

    return result

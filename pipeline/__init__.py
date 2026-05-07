"""
pipeline/ — Judgment AI extraction + planning package.

Public API
----------
run_pipeline(pdf_path)        →  ExtractionResult   full 4-step pipeline
extract(pdf_path)             →  ExtractionResult   backward-compat alias (used by app.py)
result_to_ui_dict(result)     →  dict              shape consumed by Streamlit UI
"""
from datetime import datetime, timedelta

from .main_pipeline import run_pipeline


def extract(pdf_path):
    """Backward-compatible entry point preserved for app.py's `pipeline.extract()` call."""
    return run_pipeline(pdf_path)


def result_to_ui_dict(result) -> dict:
    """Convert an ``ExtractionResult`` into the JSON shape ``app.py`` consumes.

    Mirrors the schema in ``data/judgment_data.json`` so the Streamlit UI can
    render an uploaded judgment without code changes.
    """
    def _val(name, default=None):
        f = result.get(name)
        return f.value if f is not None else default

    def _conf(name, default=80):
        f = result.get(name)
        return f.confidence if f is not None else default

    appeal_days = int(_val("appeal_timeline", 90) or 90)
    deadline = (datetime.now() + timedelta(days=appeal_days)).strftime("%Y-%m-%d")
    if result.action_plan:
        deadline = result.action_plan.get("deadline_date", deadline)

    authorities = _val("responsible_authority", []) or []
    if isinstance(authorities, str):
        authorities = [a.strip() for a in authorities.split(",") if a.strip()]

    directions = _val("key_directions", []) or []
    if isinstance(directions, str):
        directions = [directions]

    return {
        "case_title":     _val("case_title", "") or "",
        "court":          _val("court", "") or "",
        "judgment_date":  _val("judgment_date", "") or "",
        "case_number":    _val("case_number", "") or "",
        "judgment_summary": _val("judgment_summary", "") or "",
        "key_directions": list(directions),
        "responsible_authority": list(authorities),
        "action_type":    _val("action_type", "Judgment outcome recorded") or "Judgment outcome recorded",
        "appeal_timeline": {
            "type":  "inferred",
            "value_days":   appeal_days,
            "deadline_date": deadline,
            "label": "Estimated appeal deadline for dashboard countdown",
            "note":  "Inferred appeal window — verify against statutory rules.",
        },
        "verification_status": {
            "current_state": "draft",
            "human_review_required": True,
            "publishable_to_dashboard": False,
        },
        "confidence": {
            "case_title":            _conf("case_title"),
            "court":                 _conf("court"),
            "judgment_date":         _conf("judgment_date"),
            "case_number":           _conf("case_number"),
            "judgment_summary":      _conf("judgment_summary"),
            "key_directions":        _conf("key_directions"),
            "responsible_authority": _conf("responsible_authority"),
            "action_type":           _conf("action_type"),
            "appeal_timeline":       _conf("appeal_timeline", 70),
        },
        "source_highlights": {},
    }


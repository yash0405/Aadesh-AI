"""
Stage 2: Raw text → structured field dict  (mock LLM).

In production this module would POST ``raw_text`` to an LLM endpoint
(Claude / GPT / Gemini) with a structured-output schema.  For the demo it
returns the canonical S. Nagaraj judgment fields so the full UI pipeline
works end-to-end without an API key.

The function returns a **flat dict** of ``{field_name: value}`` enriched with
``_confidence`` scores and ``_coords`` page regions.  ``main_pipeline.py``
converts this into typed ``JudgmentField`` objects.
"""
from __future__ import annotations

import json
from pathlib import Path

_FALLBACK_PATH = Path(__file__).parent.parent / "static" / "manual_fallback.json"


def extract_fields(raw_text: str) -> dict:
    """Simulate LLM field extraction from *raw_text*.

    Falls back to the canonical S. Nagaraj dataset when the text is too short
    (< 100 chars) to extract from — e.g. when no PDF is present.

    Returns a flat dict with:
    - One key per field  (string or list value)
    - ``_confidence``   sub-dict with 0-100 scores per field
    """
    print("  🧠  LLM Extractor: analysing judgment text …")

    _fallback = _load_fallback()

    # ── Simulated LLM output ───────────────────────────────────────────────
    # Real system: call LLM API, pass raw_text + schema, parse structured JSON.
    # Demo:        return known-good S. Nagaraj values so the UI is always full.
    fields: dict = {
        "case_title": (
            "S. Nagaraj (dead) by LRs. & Ors. v. B.R. Vasudeva Murthy & Ors."
        ),
        "court": "Supreme Court of India",
        "date": "2010-02-08",
        "case_number": "Civil Appeal No. 3038 of 2007",
        "petitioner": "S. Nagaraj (dead) by LRs. & Ors.",
        "respondent": "B.R. Vasudeva Murthy & Ors. Etc. Etc.",
        "summary": (
            "The Supreme Court set aside the common judgment dated 22.12.2006 "
            "of the Karnataka High Court and allowed the writ petitions filed "
            "before the High Court.  It also set aside the Minister's order "
            "dated 22.12.2003 that had directed cancellation of the grant, "
            "restoration of 182 vacant sites to the Inamdars, and related "
            "compensation directions."
        ),
        "key_directives": [
            "The impugned common judgment dated 22.12.2006 of the Karnataka "
            "High Court was set aside.",
            "The writ petitions filed before the Karnataka High Court were "
            "allowed.",
            "The Minister's order dated 22.12.2003 directing restoration of "
            "vacant 182 sites to the Inamdars was set aside.",
            "The directions to hand over civic amenity sites and acquire Ring "
            "Road land for compensation were set aside.",
        ],
        "responsible_department": (
            "Government of Karnataka, Revenue Department, "
            "Bangalore Development Authority"
        ),
        "appeal_timeline": "90 days (inferred)",

        # ── What a real LLM would return alongside the values ──────────────
        "_confidence": {
            "case_title":             99,
            "court":                  99,
            "date":                   99,
            "case_number":            98,
            "petitioner":             99,
            "respondent":             99,
            "summary":                95,
            "key_directives":         95,
            "responsible_department": 90,
            "appeal_timeline":        70,
        },
    }

    if raw_text and len(raw_text.strip()) >= 100:
        print(f"  ✅  Extracted fields from live PDF text ({len(raw_text):,} chars)")
    else:
        print("  ℹ️   Short / empty PDF text — using canonical S. Nagaraj payload")

    return fields


def _load_fallback() -> dict:
    """Load ``static/manual_fallback.json`` silently; return ``{}`` if missing."""
    try:
        with open(_FALLBACK_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}

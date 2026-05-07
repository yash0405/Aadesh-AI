#!/usr/bin/env python3
"""
demo_pipeline.py — Stand-alone end-to-end pipeline demo.

Runs the full  PDF → Text → LLM Extract → LLM Plan  pipeline and prints
the structured result.  No Streamlit required.

Usage
-----
    python demo_pipeline.py                          # uses data/nagaraj_judgment.pdf
    python demo_pipeline.py path/to/other.pdf        # any judgment PDF
"""
from __future__ import annotations

import sys
from pathlib import Path

# ── Resolve PDF path ───────────────────────────────────────────────────────
_default_pdf = Path("data") / "nagaraj_judgment.pdf"
_fallback_pdf = Path("SC-Judgement.pdf")

if len(sys.argv) > 1:
    pdf_path = Path(sys.argv[1])
elif _default_pdf.exists():
    pdf_path = _default_pdf
elif _fallback_pdf.exists():
    pdf_path = _fallback_pdf
    print(f"ℹ️  data/nagaraj_judgment.pdf not found — using {_fallback_pdf}")
else:
    pdf_path = _default_pdf   # pipeline handles missing PDF gracefully

# ── Run pipeline ───────────────────────────────────────────────────────────
from pipeline.main_pipeline import run_pipeline  # noqa: E402

result = run_pipeline(pdf_path)

# ── Print summary ──────────────────────────────────────────────────────────
print("\nFULL PIPELINE RESULT")
print("=" * 58)
print(f"  📄  Fields extracted  : {len(result.fields)}")
print(f"  🎯  Action priority   : {result.action_plan['priority']}")
print(f"  📅  Appeal deadline   : {result.action_plan['deadline_date']}")
print(f"  ⚠️   Risk level        : {result.action_plan['risk_level']}")
print()
print("  Confidence scores:")
for field, score in result.confidence_map().items():
    bar = "█" * (score // 10) + "░" * (10 - score // 10)
    print(f"    {field:<24} {bar} {score}%")
print()
print("  Next steps:")
for step in result.action_plan.get("next_steps", []):
    print(f"    • {step}")
print("=" * 58)

# ── Full JSON dump ─────────────────────────────────────────────────────────
print("\n--- model_dump_json (indent=2) ---")
print(result.model_dump_json(indent=2))

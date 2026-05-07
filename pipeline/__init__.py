"""
pipeline/ — Judgment AI extraction + planning package.

Public API
----------
run_pipeline(pdf_path)  →  ExtractionResult   full 4-step pipeline
extract(pdf_path)       →  ExtractionResult   backward-compat alias (used by app.py)

Flow
----
  PDF file
    │  [1] pdf_processor.extract_text()
    ▼
  Raw text
    │  [2] llm_extractor.extract_fields()
    ▼
  Field dict  (flat values + confidence scores)
    │  [3] llm_planner.generate_action_plan()
    ▼
  Action plan dict
    │  [4] _build_extraction_result()  →  Pydantic validation
    ▼
  ExtractionResult  (with action_plan attached)
"""
from .main_pipeline import run_pipeline


def extract(pdf_path):
    """Backward-compatible entry point preserved for app.py's `pipeline.extract()` call."""
    return run_pipeline(pdf_path)

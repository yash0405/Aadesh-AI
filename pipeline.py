"""
PDF → structured-JSON orchestrator.

`extract(pdf_path)` is the single entry point used by the Streamlit app.  It
hides whatever extraction strategy is in use (mock, real LLM, OCR fallback)
behind a stable `ExtractionResult` contract.
"""
from __future__ import annotations

from pathlib import Path

import extractor
from models import ExtractionResult


def extract(pdf_path: str | Path) -> ExtractionResult:
    """Run the extraction pipeline against a PDF and return validated fields.

    The mock extractor ignores the file contents, but we still verify the path
    exists so the UI surfaces a clear error if the PDF is missing.
    """
    p = Path(pdf_path)
    if not p.exists():
        raise FileNotFoundError(f"PDF not found: {p}")

    # 1. (Mock) LLM extraction → raw structured payload
    result = extractor.generate_json(str(p))

    # 2. Pydantic re-validation acts as the schema gate
    return ExtractionResult.model_validate(result.model_dump())

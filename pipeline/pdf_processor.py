"""
Stage 1: PDF → raw text.

Uses PyMuPDF (fitz) for fast, layout-aware text extraction.
Falls back to an empty string (+ console warning) if PyMuPDF is missing or
the file is not found, so the rest of the pipeline can continue using the
static fallback data in ``static/manual_fallback.json``.
"""
from __future__ import annotations

from pathlib import Path


def extract_text(pdf_path: str, max_pages: int | None = None) -> str:
    """Return concatenated text from *pdf_path*.

    Parameters
    ----------
    pdf_path:   Path to the PDF file.
    max_pages:  Page cap (``None`` = all pages, ``3`` = first 3, etc.).

    Returns
    -------
    str  —  concatenated page text, or ``""`` on any failure.
    """
    p = Path(pdf_path)
    if not p.exists():
        print(f"  ⚠️   PDF not found: {p}  → pipeline will use static fallback")
        return ""

    try:
        import fitz  # PyMuPDF
    except ModuleNotFoundError:
        print("  ⚠️   PyMuPDF not installed (pip install pymupdf)"
              "  → pipeline will use static fallback")
        return ""

    try:
        doc = fitz.open(str(p))
        n = len(doc)
        limit = n if max_pages is None else min(max_pages, n)
        chunks: list[str] = []
        for i in range(limit):
            chunks.append(doc[i].get_text())
        doc.close()
        full_text = "\n".join(chunks)
        print(f"  📄  Extracted {len(full_text):,} chars from {limit}/{n} pages")
        return full_text
    except Exception as exc:
        print(f"  ⚠️   PyMuPDF read error ({exc})  → using static fallback")
        return ""

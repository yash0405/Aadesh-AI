# Aadesh AI — CCMS Court Judgment Action Planner

> Turn a court judgment PDF into a structured, human-verifiable action plan for the **Court Case Monitoring System (CCMS)**.

```
PDF ─► Extract Text ─► LLM Fields ─► LLM Action Plan ─► HITL Verify ─► Dashboard
```

A 1-click pipeline + court-themed Streamlit UI that lets a human reviewer verify every extracted field against the source PDF (with page-level highlights and confidence badges) before publishing to the CCMS dashboard.

---

## Quick start

```bash
# 1. Set up environment
python -m venv myenv
source myenv/bin/activate          # Windows: myenv\Scripts\activate
pip install -r requirements.txt

# 2. Run the Streamlit UI
streamlit run app.py
```

The app opens at <http://localhost:8501>.

---

## Project layout

```
.
├── app.py                       # Streamlit 3-step UI (Review → Plan → Dashboard)
├── models.py                    # Pydantic schema (JudgmentField, SourceCoord, ExtractionResult)
│
├── pipeline/                    # AI processing pipeline (package)
│   ├── __init__.py              #   exposes run_pipeline() and extract()
│   ├── pdf_processor.py         #   [1] PyMuPDF → raw text
│   ├── llm_extractor.py         #   [2] LLM (mock) → structured field dict
│   ├── llm_planner.py           #   [3] LLM (mock) → action plan dict
│   └── main_pipeline.py         #   [4] orchestrator + Pydantic validation
│
├── utils/                       # UI helpers (package)
│   ├── __init__.py              #   re-exports highlight + badge helpers
│   └── highlights.py            #   generate_highlights(result, selected_field)
│
├── data/
│   ├── SC-Judgement.pdf         #   demo judgment PDF
│   ├── nagaraj_judgment.pdf     #   alternate demo PDF
│   └── judgment_data.json       #   canonical fallback payload
│
├── static/
│   └── manual_fallback.json     #   fallback JSON when no PDF is provided
│
└── requirements.txt
```

> Note: `pipeline.py`, `extractor.py`, and `utils.py` at the repo root are the **legacy single-file modules** kept for backward compatibility. The current implementation lives in the `pipeline/` and `utils/` packages.

---

## Pipeline architecture

```
data/SC-Judgement.pdf
  │
  │  [1] pipeline/pdf_processor.py     (PyMuPDF)
  ▼
  Raw text
  │
  │  [2] pipeline/llm_extractor.py     ("LLM 1 — extract")
  ▼
  Field dict  { case_title, court, judgment_date, key_directions, … + _confidence }
  │
  │  [3] pipeline/llm_planner.py       ("LLM 2 — plan")
  ▼
  Action plan { priority, deadline_date, next_steps, department_owner, risk_level, … }
  │
  │  [4] pipeline/main_pipeline.py     (Pydantic validation + coord enrichment)
  ▼
  ExtractionResult  ──►  app.py  ──►  HITL verify  ──►  CCMS Dashboard
```

The pipeline has a single public entry point:

```python
from pipeline import run_pipeline   # or: from pipeline import extract

result = run_pipeline("data/SC-Judgement.pdf")
print(result.action_plan["priority"])      # → "HIGH"
print(result.confidence_map())             # → {"case_title": 95, ...}
```

---

## Data contract (Pydantic)

Every extracted attribute is a `JudgmentField` with provenance:

```python
class SourceCoord(BaseModel):
    page: int                            # 0-indexed PDF page
    x: float; y: float
    width: float; height: float
    note: str | None

class JudgmentField(BaseModel):
    name: str
    value: Any                           # str | list[str] | int
    confidence: int                      # 0–100
    source_coords: list[SourceCoord]
    is_inferred: bool = False

class ExtractionResult(BaseModel):
    fields: list[JudgmentField]
    action_plan: dict | None = None      # populated by llm_planner
```

`SourceCoord` rectangles drive the yellow highlight overlays in the PDF viewer and let the UI jump to the page that backs each field.

---

## Streamlit UI flow

1. **Step 1 — Review & Verify**
   - The pipeline runs on first load (results are cached).
   - Click **🔁 Re-extract from PDF** to re-run `run_pipeline()`.
   - Each field exposes a **📑 p.N** button that overlays its `source_coords` on the PDF and scrolls to that page.
   - Confidence badges: 🟢 ≥90  /  🟡 ≥70  /  🔴 <70.
   - Edit any field inline, then **✅ Approve & Continue**.
2. **Step 2 — Action Plan** — table of directions, department owner, priority, risk, and appeal deadline.
3. **Step 3 — CCMS Dashboard** — the published, human-verified record.

---

## Replacing the mock LLMs

Both LLM stages are isolated single functions with stable signatures:

| Stage   | Function                                                  | Drop-in replacement |
| ------- | --------------------------------------------------------- | ------------------- |
| Extract | `pipeline.llm_extractor.extract_fields(text) -> dict`     | Real call to Claude / GPT / Gemini returning the same flat dict shape (including `_confidence`). |
| Plan    | `pipeline.llm_planner.generate_action_plan(fields) -> dict` | Real planning LLM or rules engine returning the same action-plan shape. |

The Pydantic re-validation in [pipeline/main_pipeline.py](pipeline/main_pipeline.py) (`_build_result()`) enforces the schema contract, so any drift in the new LLM output is caught immediately rather than silently breaking the UI.

---

## Requirements

See [requirements.txt](requirements.txt):

- `streamlit` — UI framework
- `streamlit-pdf-viewer` — embedded PDF viewer with highlight overlays
- `pymupdf` — PDF text extraction
- `pydantic` — schema validation
- `pandas` — action-plan tables

Python 3.10+ recommended.

---

## License

Internal MVP. See repository owner for licensing terms.

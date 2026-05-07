# Aadesh AI — CCMS Court Judgment Action Planner

> **Real flow:**  PDF → Extract Text → LLM Fields → LLM Action Plan → HITL Verify → Dashboard

## 30-second demo

```bash
pip install -r requirements.txt
streamlit run app.py          # full UI
python demo_pipeline.py       # headless pipeline test
```

## Folder structure

```
.
├── app.py                    # Streamlit 3-step UI (Review → Plan → Dashboard)
├── pipeline/                 # AI Processing Pipeline
│   ├── __init__.py           # package; exposes extract() for app.py
│   ├── pdf_processor.py      # [1] PyMuPDF → raw text
│   ├── llm_extractor.py      # [2] mock LLM → structured field dict
│   ├── llm_planner.py        # [3] mock LLM → action plan JSON
│   └── main_pipeline.py      # [4] orchestrator → ExtractionResult
├── utils/
│   ├── __init__.py           # re-exports all original utils (backward-compat)
│   └── highlights.py         # generate_highlights(result, selected_field)
├── models.py                 # Pydantic schema: JudgmentField, ExtractionResult
├── static/
│   └── manual_fallback.json  # canonical S. Nagaraj JSON (fallback if no PDF)
├── data/
│   └── nagaraj_judgment.pdf  # demo judgment PDF
├── demo_pipeline.py          # headless end-to-end test
└── requirements.txt
```

## Pipeline architecture

```
data/nagaraj_judgment.pdf
  │
  │  [1] pipeline/pdf_processor.py  (PyMuPDF)
  ▼
  Raw text
  │
  │  [2] pipeline/llm_extractor.py  ("LLM 1 — extract")
  ▼
  Field dict  { case_title, court, date, key_directives, … + _confidence }
  │
  │  [3] pipeline/llm_planner.py    ("LLM 2 — plan")
  ▼
  Action plan { priority, deadline, next_steps, department_owner, … }
  │
  │  [4] pipeline/main_pipeline.py  (Pydantic validation + coord enrichment)
  ▼
  ExtractionResult  ──►  app.py  ──►  HITL verify  ──►  CCMS Dashboard
```

## Replacing the mock LLMs

Both `llm_extractor.extract_fields()` and `llm_planner.generate_action_plan()`
are single functions with clean signatures.  Drop in a real LLM call (Claude /
GPT / Gemini) that returns the same dict shape — nothing else needs to change.

The Pydantic re-validation in `main_pipeline._build_result()` enforces the
schema contract and will surface any field mismatches immediately.

## Pydantic contract

```python
class JudgmentField(BaseModel):
    name: str
    value: Any                      # str | list[str] | int
    confidence: int                 # 0–100
    source_coords: list[SourceCoord]
    is_inferred: bool = False

class ExtractionResult(BaseModel):
    fields: list[JudgmentField]
    action_plan: dict | None = None  # populated by llm_planner
```


A 1-click pipeline that turns a court judgment PDF into a structured,
human-verifiable action plan for the **Court Case Monitoring System (CCMS)**.

```
PDF  ─►  pipeline.extract()  ─►  ExtractionResult (Pydantic)
                                          │
                                          ▼
                          Streamlit review UI  (highlight + edit)
                                          │
                                          ▼
                              Approved Action Plan  ─►  CCMS Dashboard
```

## Files

| File              | Role                                                                |
| ----------------- | ------------------------------------------------------------------- |
| `app.py`          | Streamlit UI (3-step stepper: Review → Plan → Dashboard)            |
| `pipeline.py`     | `extract(pdf_path)` — single entry point for the whole pipeline     |
| `extractor.py`    | Mock LLM that returns the canonical S. Nagaraj judgment payload     |
| `models.py`       | Pydantic schema: `JudgmentField`, `SourceCoord`, `ExtractionResult` |
| `utils.py`        | Confidence badges + PDF highlight-overlay helpers                   |
| `SC-Judgement.pdf`| The demo judgment used by the extractor                             |

## Run

```bash
python -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Pipeline contract

Each extracted attribute is a `JudgmentField`:

```python
class JudgmentField(BaseModel):
    name: str
    value: Any                      # str | list[str] | int
    confidence: int                 # 0–100
    source_coords: list[SourceCoord]
    is_inferred: bool = False
```

`SourceCoord` is a `(page, x, y, width, height, note)` rectangle — the UI uses
it to render yellow highlight boxes and jump the PDF viewer to the right page.

## Demo flow

1. **Step 1 — Review & Verify**
   - The pipeline runs automatically on first load (cached).
   - Click **🔁 Re-extract from PDF** at any time to re-run `pipeline.extract()`.
   - Each field has a **📑 p.N** button — clicking it overlays the field's
     `source_coords` on the PDF and scrolls to that page.
   - Confidence badges (🟢 ≥90 / 🟡 ≥70 / 🔴 <70) come from `utils.confidence_badge`.
   - Edit any field, then **✅ Approve & Continue**.
2. **Step 2 — Action Plan** — generated table of directions + appeal deadline.
3. **Step 3 — CCMS Dashboard** — published, human-verified record.

## Replacing the mock extractor

Swap `extractor.generate_json` with a real LLM call (Claude / GPT / Gemini)
that returns the same `ExtractionResult` shape — nothing else in the app
needs to change. The Pydantic re-validation in `pipeline.extract` enforces
the contract.

"""
Aadesh AI — CCMS Court Judgment Action Planner
Court-themed Streamlit MVP. Step-driven navigation (no st.tabs) so we can
programmatically advance from Python on Approve / Publish.
"""
import json
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path

import utils
from models import SourceCoord

try:
    from streamlit_pdf_viewer import pdf_viewer as _pdf_viewer
    _PDF_OK = True
except ImportError:
    _PDF_OK = False

# ── File locations ────────────────────────────────────────────────────────
# Both source files live in data/ so the project root stays clean.
PDF_PATH  = Path("data/SC-Judgement.pdf")
JSON_PATH = Path("data/judgment_data.json")

st.set_page_config(
    layout="wide",
    page_title="Aadesh AI · CCMS",
    page_icon="⚖️",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════════════
# THEME
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --navy:    #0a1f3d;
    --navy-2:  #16335c;
    --navy-3:  #21477a;
    --gold:    #c9a14a;
    --gold-2:  #e7c46d;
    --gold-3:  #fce9b6;
    --ivory:   #f6f1e3;
    --paper:   #ffffff;
    --ink:     #0a1f3d;
    --mute:    #5b6470;
    --line:    #d9cfb7;
    --ok:      #1e6f31;
    --warn:    #b76e00;
    --bad:     #a41818;
    --header-h: 88px;
    --stepper-h: 60px;
    --pad-y: 14px;
    --side-pad: clamp(0.6rem, 2vw, 1.6rem);
}

/* base — fixed header pinned, body scrolls if needed */
html, body { height: 100%; margin: 0 !important; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--ink); }
.stApp { background: var(--ivory); }

header[data-testid="stHeader"], footer, #MainMenu,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; height: 0 !important; }

/* the page body — scrolls vertically below the fixed header + stepper */
.main .block-container, [data-testid="stMainBlockContainer"] {
    padding: calc(var(--header-h) + var(--stepper-h) + var(--pad-y)) var(--side-pad) calc(var(--pad-y) * 2) var(--side-pad) !important;
    max-width: 100% !important;
}

/* thin gold scrollbar on the main page */
[data-testid="stAppViewContainer"]::-webkit-scrollbar,
[data-testid="stMain"]::-webkit-scrollbar,
.main::-webkit-scrollbar { width: 8px; }
[data-testid="stAppViewContainer"]::-webkit-scrollbar-thumb,
[data-testid="stMain"]::-webkit-scrollbar-thumb,
.main::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 4px; }
[data-testid="stAppViewContainer"]::-webkit-scrollbar-track,
[data-testid="stMain"]::-webkit-scrollbar-track,
.main::-webkit-scrollbar-track { background: rgba(217,207,183,.3); }

/* PDF viewer iframe — responsive height */
.pdf-frame iframe { height: clamp(420px, calc(100vh - 260px), 720px) !important; width: 100% !important; }
.pdf-frame { width: 100%; }

/* Edit-panel internal scroll container (st.container with height) —
   Streamlit handles its own height; just style the scrollbar. */
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] *::-webkit-scrollbar { width: 6px; }
[data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"] *::-webkit-scrollbar-thumb { background: var(--gold); border-radius: 3px; }

/* Streamlit horizontal blocks: allow wrapping on small screens */
[data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; gap: 0.6rem !important; }
[data-testid="stColumn"] { min-width: 0 !important; }

/* ── RESPONSIVE BREAKPOINTS ─────────────────────────────── */

/* Tablet & below: stack the two-column review layout */
@media (max-width: 992px) {
    :root { --header-h: 110px; }
    [data-testid="stColumn"] {
        flex: 1 1 100% !important;
        width: 100% !important;
    }
    .pdf-frame iframe {
        height: 60vh !important; min-height: 360px !important;
    }
    /* Compact stepper: hide labels, show numbers only, single row */
    .step { padding: 6px 10px !important; font-size: .8rem !important; gap: 6px !important; }
    .step span.label { display: none !important; }
    .step-sep { width: 22px !important; }
}

/* Mobile: compact header, hide stepper labels (show numbers only) */
@media (max-width: 640px) {
    :root { --header-h: 130px; --side-pad: 0.7rem; }
    .court-header {
        flex-direction: column !important;
        height: auto !important;
        min-height: 130px;
        padding: 8px 12px !important;
        gap: 6px !important;
        text-align: center;
    }
    .court-header .left, .court-header .right { justify-content: center; align-items: center; }
    .court-header .center { border: none !important; padding: 0 !important; }
    .court-header .seal { width: 40px; height: 40px; font-size: 22px; }
    .court-header .brand { font-size: 1.4rem !important; }
    .court-header .sub { font-size: .62rem !important; letter-spacing: .15em !important; }
    .court-header .case-name { font-size: .95rem !important; }
    .court-header .case-info { font-size: .65rem !important; }
    .court-header .right { flex-direction: row !important; gap: 6px !important; }

    .stepper { padding: 4px 6px !important; }
    .step { padding: 6px 8px !important; font-size: .72rem !important; gap: 6px !important; }
    .step span.label { display: none; }                 /* labels hidden, show numbers */
    .step-sep { width: 18px !important; }

    .sect-title { font-size: 1.05rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.15rem !important; }
    div[data-testid="stButton"] button[kind="primary"] { font-size: .72rem !important; height: 42px !important; }
}

/* Very small phones: shrink stepper further */
@media (max-width: 380px) {
    .step .num { width: 22px !important; height: 22px !important; font-size: .8rem !important; }
    .step-sep { width: 10px !important; }
}

/* ── FIXED court header (truly pinned) ─────────────────────────────── */
.court-header {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 999;
    height: var(--header-h);
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-2) 60%, var(--navy-3) 100%);
    border-bottom: 4px solid var(--gold);
    color: var(--ivory);
    padding: 12px 28px;
    box-shadow: 0 6px 22px rgba(10,31,61,.35);
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.5rem;
}
.court-header .left { display:flex; align-items:center; gap:14px; }
.court-header .seal {
    width: 56px; height: 56px;
    border-radius: 50%;
    border: 2px solid var(--gold);
    display: flex; align-items: center; justify-content: center;
    font-size: 28px;
    background: radial-gradient(circle at 30% 30%, var(--navy-3), var(--navy));
    box-shadow: 0 0 14px rgba(231,196,109,.35), inset 0 0 8px rgba(0,0,0,.45);
}
.court-header .brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1.3rem, 2.4vw, 1.95rem); font-weight: 800; line-height: 1;
    color: var(--gold-2); letter-spacing: .03em;
    text-shadow: 0 1px 0 rgba(0,0,0,.4);
    white-space: nowrap;
}
.court-header .sub {
    font-size: .72rem; font-weight: 600;
    color: rgba(252,233,182,.78);
    letter-spacing: .22em; text-transform: uppercase;
    margin-top: 4px;
}
.court-header .center {
    flex: 1; text-align: center; padding: 0 1rem;
    border-left: 1px solid rgba(231,196,109,.22);
    border-right: 1px solid rgba(231,196,109,.22);
}
.court-header .tagline {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(1rem, 1.6vw, 1.25rem); font-weight: 700;
    color: var(--gold-2); line-height: 1.2; letter-spacing: .04em;
    font-style: italic;
}
.court-header .tagline-sub {
    font-size: clamp(.62rem, 1vw, .74rem);
    color: rgba(246,241,227,.78);
    margin-top: 5px; letter-spacing: .22em; text-transform: uppercase; font-weight: 600;
}
.court-header .right { text-align: right; display:flex; flex-direction: column; gap: 6px; align-items: flex-end; }

/* ── Case identity band (dynamic, sits below stepper) ─────────── */
.case-band {
    background: linear-gradient(90deg, rgba(10,31,61,.04) 0%, rgba(231,196,109,.10) 50%, rgba(10,31,61,.04) 100%);
    border: 1px solid var(--line);
    border-left: 4px solid var(--gold);
    border-radius: 8px;
    padding: 10px 16px;
    margin: 0 0 .9rem 0;
    display: flex; align-items: center; justify-content: space-between;
    gap: 1rem; flex-wrap: wrap;
}
.case-band .case-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(.95rem, 1.5vw, 1.15rem); font-weight: 700;
    color: var(--navy); line-height: 1.25;
}
.case-band .case-meta {
    font-size: .72rem; color: var(--mute);
    letter-spacing: .04em; margin-top: 2px;
}

.pill {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 11px; border-radius: 999px;
    font-size: .7rem; font-weight: 700;
    letter-spacing: .08em; text-transform: uppercase;
    border: 1px solid; white-space: nowrap;
}
.pill-pending  { background: rgba(231,196,109,.14); color: var(--gold-2); border-color: var(--gold); }
.pill-verified { background: rgba(46,184,87,.14);   color: #7ee7a0;       border-color: #4cae65; }
.pill-rejected { background: rgba(255,99,99,.15);   color: #ff9b9b;       border-color: #ff6e6e; }
.pill-info     { background: rgba(231,196,109,.14); color: var(--gold-2); border-color: var(--gold); }

/* ── Stepper (fixed band under the court header) ─────────────── */
.stepper {
    position: fixed;
    top: var(--header-h);
    left: var(--side-pad);
    right: var(--side-pad);
    z-index: 900;
    display: flex; align-items: center; justify-content: center;
    gap: 0;
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 6px 12px;
    box-shadow: 0 6px 18px rgba(10,31,61,.14);
    flex-wrap: wrap;
    height: var(--stepper-h);
    box-sizing: border-box;
}
.step {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 18px;
    color: var(--mute);
    font-weight: 600; font-size: .88rem;
    cursor: default;
    border-radius: 6px;
    transition: all .2s ease;
}
.step .num {
    width: 28px; height: 28px; border-radius: 50%;
    border: 2px solid var(--line);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1rem; font-weight: 700;
    background: var(--paper);
    color: var(--mute);
}
.step.active   { color: var(--navy); background: rgba(201,161,74,.12); }
.step.active .num { border-color: var(--gold); background: var(--gold); color: var(--navy); box-shadow: 0 0 0 4px rgba(201,161,74,.18); }
.step.done .num { border-color: var(--ok); background: var(--ok); color: #fff; }
.step.done     { color: var(--ok); }
.step-sep {
    width: 60px; height: 2px;
    background: var(--line);
    margin: 0 4px;
}
.step-sep.done { background: var(--ok); }

/* ── Section title ───────────────────────────────────────────────── */
.sect-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem; font-weight: 700;
    color: var(--navy);
    margin: 4px 0 10px 0;
    border-left: 3px solid var(--gold);
    padding-left: 12px;
    line-height: 1.3;
}

/* ── PDF panel ───────────────────────────────────────────────────── */
.pdf-frame {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 8px;
    box-shadow: 0 2px 10px rgba(10,31,61,.07);
}

/* ── Field label + badge ─────────────────────────────────────────── */
.field-row {
    display: flex; align-items: baseline; justify-content: space-between;
    margin: 14px 0 6px 0;
}
.field-label {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 700; font-size: 1.05rem;
    color: var(--navy);
}
.badge {
    display: inline-block;
    padding: 2px 9px; border-radius: 10px;
    font-size: .7rem; font-weight: 800;
    margin-left: 8px; vertical-align: middle;
    border: 1px solid transparent;
}
.badge-high { background: #d6f3df; color: #155f2a; border-color: #9fe0b4; }
.badge-med  { background: #fce6c2; color: #7a4900; border-color: #efc784; }
.badge-low  { background: #fad4d4; color: #7a0d0d; border-color: #f1a3a3; }

/* ── Inputs (high contrast white) ────────────────────────────────── */
div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea,
div[data-baseweb="select"] > div {
    background: var(--paper) !important;
    color: var(--ink) !important;
    border-radius: 6px !important;
    border: 1px solid var(--line) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .94rem !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 2px rgba(201,161,74,.25) !important;
}
[data-testid="stNumberInput"] button {
    background: var(--ivory) !important; color: var(--navy) !important;
    border-color: var(--line) !important;
}
[data-baseweb="tag"] {
    background: var(--navy) !important;
    color: var(--gold-2) !important;
    border: 1px solid var(--gold) !important;
}

/* ── Buttons ─────────────────────────────────────────────────────── */
div[data-testid="stButton"] button[kind="secondary"] {
    background: var(--paper);
    color: var(--navy);
    border: 1px solid var(--gold);
    border-radius: 18px;
    padding: 2px 12px;
    font-size: .74rem; font-weight: 600;
    line-height: 1.4;
    min-height: 0; height: 32px;
    transition: all .18s ease;
    box-shadow: 0 1px 2px rgba(10,31,61,.06);
}
div[data-testid="stButton"] button[kind="secondary"]:hover {
    background: var(--gold);
    color: var(--navy);
    border-color: var(--gold-2);
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(201,161,74,.4);
}
div[data-testid="stButton"] button[kind="primary"] {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-2) 100%);
    color: var(--gold-2) !important;
    border: 1px solid var(--gold);
    border-radius: 6px;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
    font-size: .85rem;
    height: 46px;
    box-shadow: 0 4px 12px rgba(10,31,61,.25);
    transition: all .2s ease;
}
div[data-testid="stButton"] button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--navy-2) 0%, var(--navy-3) 100%);
    color: #fff !important;
    border-color: var(--gold-2);
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(10,31,61,.45);
}

.action-divider { height: 1px; background: var(--line); margin: 14px 0 12px 0; }

/* ── Deadline boxes ──────────────────────────────────────────────── */
.dl-urgent {
    background: linear-gradient(135deg, #fff3f3, #ffd7d7);
    border: 2px solid var(--bad); border-radius: 10px;
    padding: 1rem 1.2rem; color: var(--bad);
    font-family: 'Cormorant Garamond', serif; font-size: 1.15rem;
    text-align: center;
    box-shadow: 0 4px 14px rgba(164,24,24,.12);
}
.dl-ok {
    background: linear-gradient(135deg, #f0fbf3, #d8f1de);
    border: 2px solid var(--ok); border-radius: 10px;
    padding: 1rem 1.2rem; color: var(--ok);
    font-family: 'Cormorant Garamond', serif; font-size: 1.15rem;
    text-align: center;
    box-shadow: 0 4px 14px rgba(30,111,49,.12);
}

/* ── Dashboard band ──────────────────────────────────────────────── */
.dash-band {
    background: linear-gradient(135deg, var(--navy), var(--navy-2));
    color: var(--ivory);
    padding: 1.1rem 1.4rem; border-radius: 10px;
    border-left: 5px solid var(--gold);
    margin-bottom: 1rem;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem; font-weight: 700;
    box-shadow: 0 6px 18px rgba(10,31,61,.22);
}

/* ── Metric cards ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--paper);
    border: 1px solid var(--line);
    border-left: 3px solid var(--gold);
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(10,31,61,.06);
}
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    font-size: .72rem !important;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--mute) !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
    font-size: 1.55rem !important;
}

/* ── Misc ────────────────────────────────────────────────────────── */
hr { border-color: var(--line) !important; margin: .5rem 0 !important; }
[data-testid="InputInstructions"] { display: none; }
[data-testid="stExpander"] summary {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}

/* native scroll panel from st.container(height=N) */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--line) !important;
    border-radius: 10px !important;
    background: rgba(255,255,255,0.55) !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 8px;
    overflow: hidden;
}
[data-baseweb="tooltip"] {
    background: var(--navy) !important;
    color: var(--gold-2) !important;
    border: 1px solid var(--gold) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .78rem !important;
    border-radius: 6px !important;
    max-width: 320px !important;
}
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, var(--gold), var(--gold-2)) !important;
}
[data-testid="stAlert"] { border-radius: 8px; border-left-width: 4px !important; }
[data-testid="stCaptionContainer"] { font-family: 'Inter', sans-serif; color: var(--mute) !important; }
</style>
""",
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════════════
# DATA — loaded directly from data/judgment_data.json
# ════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_judgment() -> dict:
    with open(JSON_PATH, "r") as fh:
        return json.load(fh)


judgment = load_judgment()
conf = judgment["confidence"]
src  = judgment["source_highlights"]

# Source-coordinate registry — maps each field to PDF bounding boxes.
# highlight_button() uses these to overlay yellow spans and scroll the viewer.
def _sc(**kw) -> SourceCoord:
    return SourceCoord(**kw)

coords_map: dict = {
    "case_title": [
        _sc(page=0, x=100, y=50, width=400, height=50, note="Page 1, heading"),
    ],
    "court": [
        _sc(page=0, x=100, y=20, width=400, height=30, note="Page 1, court banner"),
    ],
    "judgment_date": [
        _sc(page=58, x=50, y=600, width=550, height=100, note="Page 59, signature block"),
    ],
    "case_number": [
        _sc(page=0, x=100, y=120, width=400, height=40, note="Page 1, header"),
    ],
    "judgment_summary": [
        _sc(page=57, x=50, y=300, width=550, height=200, note="Pages 58-59, operative paragraphs"),
    ],
    "key_directions": [
        _sc(page=57, x=50, y=300, width=550, height=150, note="Pages 58-59, paragraphs 40-41"),
        _sc(page=58, x=50, y=80,  width=550, height=200, note="Page 59, continuation"),
    ],
    "responsible_authority": [
        _sc(page=1,  x=50, y=100, width=550, height=120, note="Pages 2-10, party listings"),
        _sc(page=56, x=50, y=400, width=550, height=120, note="Pages 57-58, operative refs"),
    ],
    "appeal_timeline": [
        _sc(page=58, x=50, y=600, width=550, height=100, note="Page 59, judgment date area"),
    ],
}


def badge(pct: int) -> str:
    return utils.confidence_badge(pct)


def field_label(label: str, pct: int):
    st.markdown(
        f'<div class="field-row"><span class="field-label">{label}{badge(pct)}</span></div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════════════════════════════════════
def _default_edits():
    return {
        "case_title":    judgment["case_title"],
        "court":         judgment["court"],
        "judgment_date": judgment["judgment_date"],
        "case_number":   judgment["case_number"],
        "summary":       judgment["judgment_summary"],
        "directions":    list(judgment["key_directions"]),
        "authority":     list(judgment["responsible_authority"]),
        "action_type":   judgment["action_type"],
        "appeal_days":   int(judgment["appeal_timeline"]["value_days"]),
    }


for k, v in {
    "edits":                 _default_edits(),
    "status":                "draft",
    "final_plan":            None,
    "published":             False,
    "highlight_page":        0,
    "highlight_annotations": [],
    "highlight_field":       None,
    "step":                  1,        # 1 = review, 2 = plan, 3 = dashboard
    "reject_reason":         "",
    "rejected_at":           None,
}.items():
    st.session_state.setdefault(k, v)

edits = st.session_state.edits


# Reject confirmation as a proper modal dialog (impossible to miss)
@st.dialog("Reject this Extraction")
def _reject_dialog():
    st.markdown(
        "<div style='font-size:.88rem;color:var(--mute);margin-bottom:8px;'>"
        "Provide a reason — this will be logged in the audit trail and the "
        "plan will be marked for re-extraction.</div>",
        unsafe_allow_html=True,
    )
    reason = st.text_area(
        "Rejection reason",
        placeholder="e.g. Wrong case extracted, key directions missing, dates incorrect…",
        key="rej_reason_input",
        height=120,
    )
    c1, c2 = st.columns(2)
    if c1.button("✅ Confirm Rejection", type="primary",
                 use_container_width=True, key="btn_rej_confirm"):
        st.session_state.status = "rejected"
        st.session_state.reject_reason = (reason or "").strip() or "No reason provided."
        st.session_state.rejected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.final_plan = None
        st.session_state.published = False
        st.toast("❌ Plan rejected", icon="⚠️")
        st.rerun()
    if c2.button("Cancel", use_container_width=True, key="btn_rej_cancel"):
        st.rerun()


def highlight_button(field_name: str, label: str, key: str):
    """Per-field button that overlays yellow boxes on the PDF using source_coords."""
    if not (_PDF_OK and PDF_PATH.exists()):
        return
    coords = coords_map.get(field_name) or []
    if not coords:
        st.button("📑 —", key=key, disabled=True,
                  help=f"No source coordinates for {label}")
        return
    page = utils.first_page(coords)
    notes = " | ".join(c.note for c in coords if c.note) or "Extracted span"
    tip = (f"📍 {label}\n\nSource: {notes}\n\n"
           f"Click → scroll to p.{page + 1} and highlight {len(coords)} region(s)")
    if st.button(f"📑 p.{page + 1}", key=key, help=tip):
        st.session_state.highlight_page = page
        st.session_state.highlight_annotations = utils.highlight_coords(coords)
        st.session_state.highlight_field = field_name
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# FIXED COURT HEADER
# ════════════════════════════════════════════════════════════════════════════
status_pill = {
    "draft":    '<span class="pill pill-pending">🟡 Pending Review</span>',
    "approved": '<span class="pill pill-verified">✅ Human Verified</span>',
    "rejected": '<span class="pill pill-rejected">❌ Rejected</span>',
}[st.session_state.status]
avg_conf = int(sum(conf.values()) / len(conf))

st.markdown(
    f"""
<div class="court-header">
    <div class="left">
        <div class="seal">⚖️</div>
        <div>
            <div class="brand">Aadesh AI</div>
            <div class="sub">Court Case Monitoring System</div>
        </div>
    </div>
    <div class="center">
        <div class="tagline">“Justice, automated with diligence.”</div>
        <div class="tagline-sub">AI-Assisted Judgment Action Planner</div>
    </div>
    <div class="right">
        {status_pill}
        <span class="pill pill-info">AI Confidence {avg_conf}%</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════════════
# STEPPER (replaces st.tabs — drives navigation via session_state.step)
# ════════════════════════════════════════════════════════════════════════════
def render_stepper():
    s = st.session_state.step
    items = [(1, "Review & Verify"), (2, "Action Plan"), (3, "CCMS Dashboard")]
    html = '<div class="stepper">'
    for idx, (n, label) in enumerate(items):
        cls = "step"
        num_html = str(n)
        if n < s:
            cls += " done"; num_html = "✓"
        elif n == s:
            cls += " active"
        html += f'<div class="{cls}"><div class="num">{num_html}</div><span class="label">Step {n} · {label}</span></div>'
        if idx < len(items) - 1:
            sep_cls = "step-sep done" if (n < s) else "step-sep"
            html += f'<div class="{sep_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


render_stepper()


# ── Dynamic case-identity band (below stepper, updates per PDF) ───────────
if judgment.get("case_title"):
    st.markdown(
        f"""
<div class="case-band">
    <div>
        <div class="case-title">📜 {judgment['case_title']}</div>
        <div class="case-meta">
            {judgment.get('court', '—')} &nbsp;·&nbsp;
            {judgment.get('case_number', '—')} &nbsp;·&nbsp;
            Judgment dated {judgment.get('judgment_date', '—')}
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# STEP 1 — REVIEW & VERIFY
# ════════════════════════════════════════════════════════════════════════════
def render_step_1():
    # ── Rejection banner ──────────────────────────────────────────────
    if st.session_state.status == "rejected":
        reason = st.session_state.reject_reason or "No reason provided."
        when   = st.session_state.rejected_at or "—"
        st.markdown(
            f"""
<div style="background:linear-gradient(135deg,#fff0f0,#ffd9d9);
            border:2px solid var(--bad);border-left:6px solid var(--bad);
            border-radius:10px;padding:14px 18px;margin:0 0 12px 0;
            box-shadow:0 4px 14px rgba(164,24,24,.15);">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="font-size:1.6rem;">❌</div>
    <div style="flex:1;">
      <div style="font-family:'Cormorant Garamond',serif;font-weight:800;
                  font-size:1.25rem;color:var(--bad);">
        Plan Rejected — Reset to review the original judgment again
      </div>
      <div style="font-size:.8rem;color:#6b1414;margin-top:2px;">
        <strong>Reason:</strong> {reason} &nbsp;·&nbsp;
        <strong>Rejected at:</strong> {when}
      </div>
    </div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("↺ Restore as Draft", use_container_width=False,
                     key="rej_restore"):
            st.session_state.status = "draft"
            st.session_state.reject_reason = ""
            st.session_state.rejected_at   = None
            st.rerun()

    col_pdf, col_edit = st.columns([1.05, 1], gap="large")

    # ── PDF (data/SC-Judgement.pdf) ──────────────────────────────────
    with col_pdf:
        st.markdown('<div class="sect-title">📜 Original Judgment</div>',
                    unsafe_allow_html=True)
        if _PDF_OK and PDF_PATH.exists():
            # Faint gold overview when no field is selected; bright yellow
            # on the field the user last clicked.
            ann = st.session_state.highlight_annotations
            if not ann:
                ann = []
                for c_list in coords_map.values():
                    ann.extend(utils.highlight_coords(
                        c_list, color="rgba(201,161,74,0.18)"))
            st.markdown('<div class="pdf-frame">', unsafe_allow_html=True)
            _pdf_viewer(
                str(PDF_PATH),
                width=700, height=560,
                pages_vertical_spacing=2,
                scroll_to_page=st.session_state.highlight_page + 1,
                annotations=ann,
            )
            st.markdown('</div>', unsafe_allow_html=True)
            cap = f"📍 Page {st.session_state.highlight_page + 1}"
            if st.session_state.highlight_field:
                cap += f" · highlighting **{st.session_state.highlight_field}**"
            st.caption(cap)
        elif _PDF_OK:
            st.info(f"📂 Place **{PDF_PATH.name}** in the `data/` folder.")
        else:
            st.warning("Install `streamlit-pdf-viewer` for inline PDF.")

    # ── Edit panel ────────────────────────────────────────────────────
    with col_edit:
        st.markdown('<div class="sect-title">✒️ Verify & Edit Extracted Data</div>',
                    unsafe_allow_html=True)

        scroll = st.container(height=480, border=True)
        with scroll:
            # Case Title
            field_label("Case Title", conf["case_title"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                edits["case_title"] = st.text_input(
                    "Case Title", value=edits["case_title"],
                    label_visibility="collapsed", key="in_ct")
            with c2:
                highlight_button("case_title", "Case Title", "j_ct")

            # Date / Number — give labels their own rows so badge isn't clipped
            field_label("Judgment Date", conf["judgment_date"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                edits["judgment_date"] = st.text_input(
                    "Date", value=edits["judgment_date"],
                    label_visibility="collapsed", key="in_jd")
            with c2:
                highlight_button("judgment_date", "Judgment Date", "j_jd")

            field_label("Case Number", conf["case_number"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                edits["case_number"] = st.text_input(
                    "No.", value=edits["case_number"],
                    label_visibility="collapsed", key="in_cn")
            with c2:
                highlight_button("case_number", "Case Number", "j_cn")

            # Summary
            field_label("Judgment Summary", conf["judgment_summary"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                edits["summary"] = st.text_area(
                    "Summary", value=edits["summary"], height=110,
                    label_visibility="collapsed", key="in_sum")
            with c2:
                highlight_button("judgment_summary", "Judgment Summary", "j_sum")

            # Directions
            field_label("Key Directions", conf["key_directions"])
            new_dirs, to_delete = [], []
            for i, d in enumerate(edits["directions"]):
                tcol, jcol, dcol = st.columns([7, 1.4, 0.7])
                with tcol:
                    val = st.text_area(
                        f"Direction {i + 1}", value=d, height=70,
                        label_visibility="collapsed", key=f"dir_{i}")
                    new_dirs.append(val)
                with jcol:
                    st.markdown("<div style='height:6px'></div>",
                                unsafe_allow_html=True)
                    highlight_button("key_directions",
                                     f"Direction {i + 1}", f"j_dir_{i}")
                with dcol:
                    st.markdown("<div style='height:6px'></div>",
                                unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_dir_{i}",
                                 help="Delete this direction"):
                        to_delete.append(i)
            if to_delete:
                edits["directions"] = [v for i, v in enumerate(new_dirs)
                                       if i not in to_delete]
                st.rerun()
            else:
                edits["directions"] = new_dirs
            if st.button("➕ Add Direction", key="add_dir"):
                edits["directions"].append("")
                st.rerun()

            # Authority
            field_label("Responsible Authorities", conf["responsible_authority"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                opts = sorted(set(judgment["responsible_authority"] + [
                    "Legal Cell", "Urban Development",
                    "Municipal Corporation", "Revenue Department"]))
                edits["authority"] = st.multiselect(
                    "Auth", options=opts, default=edits["authority"],
                    label_visibility="collapsed", key="in_auth")
            with c2:
                highlight_button("responsible_authority",
                                 "Responsible Authority", "j_auth")

            # Appeal window
            field_label("Appeal Window (days)", conf["appeal_timeline"])
            c1, c2 = st.columns([6, 1.2])
            with c1:
                edits["appeal_days"] = st.number_input(
                    "Days", value=int(edits["appeal_days"]),
                    min_value=0, max_value=365,
                    label_visibility="collapsed", key="in_days",
                    help=judgment["appeal_timeline"]["note"])
            with c2:
                highlight_button("appeal_timeline", "Appeal Timeline", "j_ap")

        # action bar (BELOW the scroll container — always visible)
        st.markdown('<div class="action-divider"></div>', unsafe_allow_html=True)
        b1, b2, b3 = st.columns([1.6, 1, 1])

        if b1.button("✅ Approve & Continue →", type="primary",
                     use_container_width=True, key="btn_appr"):
            try:
                dl = (datetime.strptime(edits["judgment_date"], "%Y-%m-%d")
                      + timedelta(days=int(edits["appeal_days"]))).strftime("%Y-%m-%d")
            except ValueError:
                dl = "—"
            st.session_state.status = "approved"
            st.session_state.final_plan = {
                **{k: edits[k] for k in edits},
                "appeal_deadline": dl,
                "ai_confidence":   conf,
                "verified_by":     "Human Reviewer",
                "verified_at":     str(datetime.now()),
            }
            st.session_state.published = False
            st.session_state.step = 2          # ← server-side advance, real
            st.toast("✅ Approved — opening Action Plan…", icon="⚖️")
            st.rerun()

        if b2.button("🔄 Reset to AI", use_container_width=True, key="btn_rst"):
            st.session_state.edits = _default_edits()
            st.session_state.status = "draft"
            st.session_state.final_plan = None
            st.session_state.published = False
            st.rerun()

        if b3.button("❌ Reject", use_container_width=True, key="btn_rej"):
            _reject_dialog()


# ════════════════════════════════════════════════════════════════════════════
# STEP 2 — ACTION PLAN
# ════════════════════════════════════════════════════════════════════════════
def render_step_2():
    if st.session_state.status == "rejected":
        st.markdown(
            '<div class="dl-urgent" style="font-size:1.1rem;">❌ '
            'This extraction was rejected. Re-extract or upload a new PDF '
            'on Step 1 to continue.</div>',
            unsafe_allow_html=True,
        )
        if st.button("← Back to Step 1", key="back_rej_2"):
            st.session_state.step = 1; st.rerun()
        return
    if st.session_state.status != "approved" or not st.session_state.final_plan:
        st.warning("⚠️ Complete Step 1 first.")
        if st.button("← Back to Review", use_container_width=False, key="back_1"):
            st.session_state.step = 1; st.rerun()
        return

    fp = st.session_state.final_plan
    st.markdown(
        f'<div class="dash-band">📋 Action Plan — {fp["case_title"]}'
        f'<div style="font-size:.78rem;font-family:Inter;color:rgba(246,241,227,.8);'
        f'letter-spacing:.08em;font-weight:500;margin-top:6px;">'
        f'VERIFIED BY {fp["verified_by"].upper()} · {fp["verified_at"][:19]}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    try:
        dl = datetime.strptime(fp["appeal_deadline"], "%Y-%m-%d").date()
        days_left = (dl - date.today()).days
    except (ValueError, TypeError):
        days_left = 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Judgment Date", fp["judgment_date"])
    m2.metric("Appeal Deadline", fp["appeal_deadline"])
    m3.metric("Days Remaining", f"{days_left}",
              delta="URGENT" if days_left < 30 else "On Track",
              delta_color="inverse" if days_left < 30 else "normal")
    avg = int(sum(fp["ai_confidence"].values()) / len(fp["ai_confidence"]))
    m4.metric("Avg AI Confidence", f"{avg}%")

    cls = "dl-urgent" if days_left < 30 else "dl-ok"
    ico = "🚨" if days_left < 30 else "✅"
    st.markdown(
        f'<div class="{cls}" style="margin:.8rem 0;">'
        f'{ico} Appeal window expires in <strong>{max(0, days_left)} days</strong>'
        f' &nbsp;·&nbsp; Deadline: <strong>{fp["appeal_deadline"]}</strong></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sect-title">📋 Required Actions</div>',
                unsafe_allow_html=True)
    auth_str = ", ".join(fp["authority"]) if fp["authority"] else "—"
    rows = []
    prio = {0: "🔴 High", 1: "🟡 Medium"}
    for i, d in enumerate(fp["directions"]):
        rows.append({"#": i + 1, "Action / Direction": d,
                     "Responsible": auth_str,
                     "Priority": prio.get(i, "🟢 Low"),
                     "Status": "⏳ Pending"})
    rows.append({
        "#": len(fp["directions"]) + 1,
        "Action / Direction": (
            f"Review appeal options and file if required within "
            f"{fp['appeal_days']} days (deadline: {fp['appeal_deadline']})"),
        "Responsible": f"Legal Cell / {fp['authority'][0] if fp['authority'] else '—'}",
        "Priority": "🔴 High" if days_left < 30 else "🟡 Medium",
        "Status": "⏳ Pending",
    })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                 column_config={
                     "#": st.column_config.NumberColumn(width="small"),
                     "Priority": st.column_config.TextColumn(width="small"),
                     "Status":   st.column_config.TextColumn(width="small"),
                 })

    st.markdown('<div class="action-divider"></div>', unsafe_allow_html=True)
    cback, cpub, _ = st.columns([1, 1.6, 1])
    if cback.button("← Back", use_container_width=True, key="bk_2"):
        st.session_state.step = 1; st.rerun()
    if cpub.button("🚀 Publish to CCMS Dashboard →", type="primary",
                   use_container_width=True, key="btn_pub"):
        st.session_state.published = True
        st.session_state.step = 3
        st.toast("✅ Published to CCMS — opening Dashboard…", icon="📊")
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# STEP 3 — DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
def render_step_3():
    if not st.session_state.final_plan:
        st.warning("⚠️ No verified records yet.")
        if st.button("← Back", key="bk3a"):
            st.session_state.step = 1; st.rerun()
        return
    if not st.session_state.published:
        st.info("ℹ️ Plan approved but not yet published.")
        if st.button("← Back to Action Plan", key="bk3b"):
            st.session_state.step = 2; st.rerun()
        return

    fp = st.session_state.final_plan
    st.markdown(
        f'<div class="dash-band">✅ Human-Verified Action Record'
        f'<div style="font-size:.85rem;color:rgba(246,241,227,.85);'
        f'font-family:Inter;font-weight:500;margin-top:6px;">{fp["case_title"]}</div></div>',
        unsafe_allow_html=True,
    )

    try:
        dl = datetime.strptime(fp["appeal_deadline"], "%Y-%m-%d").date()
        days_left = (dl - date.today()).days
    except (ValueError, TypeError):
        days_left = 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Case Number", fp["case_number"])
    k2.metric("Court", fp["court"])
    k3.metric("Appeal Deadline", fp["appeal_deadline"])
    k4.metric("Days Left", f"{days_left}",
              delta="URGENT" if days_left < 30 else "On Track",
              delta_color="inverse" if days_left < 30 else "normal")

    col_info, col_meta = st.columns([2, 1], gap="medium")
    with col_info:
        st.markdown('<div class="sect-title">📝 Case Summary</div>',
                    unsafe_allow_html=True)
        st.markdown(fp["summary"])
        st.markdown('<div class="sect-title">📌 Key Directions</div>',
                    unsafe_allow_html=True)
        for i, d in enumerate(fp["directions"]):
            ico = {0: "🔴", 1: "🟡"}.get(i, "🟢")
            st.markdown(f"{ico} **{i+1}.** {d}")

    with col_meta:
        st.markdown('<div class="sect-title">🏢 Responsible Departments</div>',
                    unsafe_allow_html=True)
        for a in fp["authority"]:
            st.markdown(f"• **{a}**")
        st.markdown('<div class="sect-title">📊 AI Confidence</div>',
                    unsafe_allow_html=True)
        for k, v in fp["ai_confidence"].items():
            lbl = k.replace("_", " ").title()
            st.progress(v / 100, text=f"{lbl}: {v}%")

    st.markdown('<div class="sect-title">📋 Department-wise Action Table</div>',
                unsafe_allow_html=True)
    auth_str = ", ".join(fp["authority"]) if fp["authority"] else "—"
    rows = []
    for i, d in enumerate(fp["directions"]):
        rows.append({
            "Direction":  d[:90] + ("…" if len(d) > 90 else ""),
            "Department": auth_str,
            "Priority":   {0: "🔴 High", 1: "🟡 Medium"}.get(i, "🟢 Low"),
            "Action Due": fp["appeal_deadline"],
            "Status":     "⏳ Pending",
        })
    rows.append({
        "Direction":  f"Decide on appeal within {fp['appeal_days']} days",
        "Department": f"Legal Cell / {fp['authority'][0] if fp['authority'] else '—'}",
        "Priority":   "🔴 High" if days_left < 30 else "🟡 Medium",
        "Action Due": fp["appeal_deadline"],
        "Status":     "⏳ Pending",
    })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("🔍 Audit Trail"):
        orig = _default_edits()
        st.json({
            "case_title_edited": fp["case_title"] != orig["case_title"],
            "summary_edited":    fp["summary"] != orig["summary"],
            "directions_edited": fp["directions"] != orig["directions"],
            "authority_edited":  set(fp["authority"]) != set(orig["authority"]),
            "timeline_edited":   fp["appeal_days"] != orig["appeal_days"],
            "verified_by":       fp["verified_by"],
            "verified_at":       fp["verified_at"],
        })

    st.markdown('<div class="action-divider"></div>', unsafe_allow_html=True)
    cb, _, _ = st.columns([1, 2, 2])
    if cb.button("← Edit Plan", use_container_width=True, key="bk_3"):
        st.session_state.step = 2; st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════════════
{1: render_step_1, 2: render_step_2, 3: render_step_3}[st.session_state.step]()

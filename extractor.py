"""
Mock LLM extractor.

In production this module would call a real LLM (Claude / GPT / Gemini) with
the PDF text + structured-output schema.  For the demo we return a hand-curated
`ExtractionResult` matching the S. Nagaraj judgment shipped with the app, so
the rest of the pipeline (validation → UI → highlighting) works end-to-end.
"""
from __future__ import annotations

from models import ExtractionResult, JudgmentField, SourceCoord


def generate_json(pdf_path: str | None = None) -> ExtractionResult:
    """Return the canonical S. Nagaraj extraction (mock LLM output)."""
    return ExtractionResult(
        fields=[
            JudgmentField(
                name="case_title",
                value="S. Nagaraj (dead) by LRs. & Ors. v. B.R. Vasudeva Murthy & Ors.",
                confidence=99,
                source_coords=[
                    SourceCoord(page=0, x=100, y=50, width=400, height=50,
                                note="Page 1, heading"),
                ],
            ),
            JudgmentField(
                name="court",
                value="Supreme Court of India",
                confidence=99,
                source_coords=[
                    SourceCoord(page=0, x=100, y=20, width=400, height=30,
                                note="Page 1, court name banner"),
                ],
            ),
            JudgmentField(
                name="judgment_date",
                value="2010-02-08",
                confidence=99,
                source_coords=[
                    SourceCoord(page=58, x=50, y=600, width=550, height=100,
                                note="Page 59, signature block"),
                ],
            ),
            JudgmentField(
                name="case_number",
                value="Civil Appeal No. 3038 of 2007",
                confidence=98,
                source_coords=[
                    SourceCoord(page=0, x=100, y=120, width=400, height=40,
                                note="Page 1, header"),
                ],
            ),
            JudgmentField(
                name="judgment_summary",
                value=(
                    "The Supreme Court set aside the common judgment dated "
                    "22.12.2006 of the Karnataka High Court and allowed the "
                    "writ petitions filed before the High Court. It also set "
                    "aside the Minister's order dated 22.12.2003 that had "
                    "directed cancellation of the grant, restoration of 182 "
                    "vacant sites to the Inamdars, and related compensation "
                    "directions."
                ),
                confidence=95,
                source_coords=[
                    SourceCoord(page=57, x=50, y=300, width=550, height=200,
                                note="Pages 58-59, final operative paragraphs"),
                ],
            ),
            JudgmentField(
                name="key_directions",
                value=[
                    "The impugned common judgment dated 22.12.2006 of the "
                    "Karnataka High Court was set aside.",
                    "The writ petitions filed before the Karnataka High Court "
                    "were allowed.",
                    "The Minister's order dated 22.12.2003 directing "
                    "restoration of vacant 182 sites to the Inamdars was set "
                    "aside.",
                    "The directions to hand over civic amenity sites and "
                    "acquire Ring Road land for compensation were set aside.",
                ],
                confidence=95,
                source_coords=[
                    SourceCoord(page=57, x=50, y=300, width=550, height=150,
                                note="Pages 58-59, paragraphs 40-41"),
                    SourceCoord(page=58, x=50, y=80, width=550, height=200,
                                note="Page 59, continuation of operative directions"),
                ],
            ),
            JudgmentField(
                name="responsible_authority",
                value=[
                    "Government of Karnataka",
                    "Revenue Department",
                    "Bangalore Development Authority",
                ],
                confidence=90,
                source_coords=[
                    SourceCoord(page=1, x=50, y=100, width=550, height=120,
                                note="Pages 2-10, party listings"),
                    SourceCoord(page=56, x=50, y=400, width=550, height=120,
                                note="Pages 57-58, operative references"),
                ],
            ),
            JudgmentField(
                name="appeal_timeline",
                value=90,
                confidence=70,
                is_inferred=True,
                source_coords=[
                    SourceCoord(page=58, x=50, y=600, width=550, height=100,
                                note="Inferred from judgment date on page 59"),
                ],
            ),
        ]
    )

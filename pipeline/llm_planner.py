"""
Stage 3: Structured fields → Action Plan JSON  (mock LLM planner).

A second "LLM pass" that reads the extracted field dict and synthesises an
action plan with priority, department ownership, next steps, and deadline.

In production this would call a planning LLM or a rules-engine microservice.
For the demo it derives the plan deterministically from the extracted fields.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta


def generate_action_plan(extracted_fields: dict) -> dict:
    """Simulate a planning LLM.

    Parameters
    ----------
    extracted_fields:
        The flat dict returned by ``llm_extractor.extract_fields()``.

    Returns
    -------
    dict  —  structured action plan ready for storage and dashboard display.
    """
    print("  📋  LLM Planner: generating action plan …")

    # ── Parse appeal window ────────────────────────────────────────────────
    appeal_days = 90
    raw_timeline = str(extracted_fields.get("appeal_timeline", "90"))
    m = re.search(r"\d+", raw_timeline)
    if m:
        appeal_days = int(m.group())

    deadline = (datetime.now() + timedelta(days=appeal_days)).strftime("%Y-%m-%d")
    days_left = appeal_days          # from today
    priority  = "HIGH" if days_left < 60 else "MEDIUM"
    risk      = "HIGH" if days_left < 30 else ("MEDIUM" if days_left < 60 else "LOW")

    dept = extracted_fields.get(
        "responsible_department", "Revenue Department, Karnataka"
    )

    plan: dict = {
        "compliance_required":  True,
        "appeal_review":        True,
        "deadline_days":        appeal_days,
        "deadline_date":        deadline,
        "priority":             priority,
        "risk_level":           risk,
        "next_steps": [
            "Review compensation quantum for the 182 affected sites",
            f"Check appeal limitation period — deadline: {deadline}",
            "Assign case to Revenue Secretary for compliance tracking",
            "Co-ordinate with Bangalore Development Authority on civic sites",
            "Update CCMS dashboard with human-verified fields",
        ],
        "department_owner":  dept,
        "estimated_effort":  "2–4 weeks",
        "generated_by":      "LLM Planner v1 (mock)",
    }

    print(
        f"  ✅  Action plan ready — priority: {priority}, "
        f"deadline: {deadline}, risk: {risk}"
    )
    return plan

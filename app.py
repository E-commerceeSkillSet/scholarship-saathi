"""Scholarship Saathi — one-file backend.

POST /api/check
  body: {
    "student_text": str, "criteria_text": str,
    "matric_pct": float|null, "fsc_pct": float|null,
    "domicile": str, "monthly_income": int|null,
    "programme": str, "university_type": str
  }
  returns: per-scheme verdicts (ELIGIBLE / LIKELY NOT / NEEDS CHECK) with
  per-rule pass/fail, probability and quoted evidence, missing-info list,
  next step, and credits used.

Uses clocked-sdk==0.7.0. The API key comes from the CLOCKED_API_KEY
environment variable on the server only. If it is not set, the endpoint
returns {"status": "needs_key", "message": "live mode needs a key — switch
to Fixtures demo"} and the frontend falls back to fixtures/ demo data.

Run:  pip install -r requirements.txt && python app.py
"""

import os

from clocked import Clocked  # clocked-sdk==0.7.0
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Scholarship Saathi")

SCHEMES = ["Honhaar", "HEC Need-Based", "PEEF"]


class CheckRequest(BaseModel):
    student_text: str
    criteria_text: str
    matric_pct: float | None = None
    fsc_pct: float | None = None
    domicile: str = ""
    monthly_income: int | None = None
    programme: str = ""
    university_type: str = ""


@app.post("/api/check")
def check(req: CheckRequest):
    api_key = os.environ.get("CLOCKED_API_KEY", "").strip()
    if not api_key:
        return {
            "status": "needs_key",
            "message": "live mode needs a key — switch to Fixtures demo",
            "credits_used": 0,
            "schemes": [],
        }

    client = Clocked(api_key)

    # 1) PII first — replace names / emails / phones before anything else.
    safe_text = client.pii(
        text=req.student_text,
        anonymize="replace",
        entities=["person", "email", "phone"],
    )

    # 2) Extract the six structured fields, verbatim, with source positions.
    extracted = client.extract(
        text=safe_text,
        fields=[
            "matric_pct",
            "fsc_pct",
            "domicile",
            "monthly_income",
            "programme",
            "university_type",
        ],
    )

    # 3) Decide — one noul question per scheme, criteria-bound, typed answer
    #    plus probability. (Per-rule questions are built from criteria_text.)
    decisions = {}
    for scheme in SCHEMES:
        decisions[scheme] = client.decide(
            question=f"Does this student meet the {scheme} criteria?",
            instructions=(
                "Answer true only when the criteria text is clearly met. "
                "Quote the exact evidence from the student or criteria text."
            ),
            criteria=req.criteria_text,
            context=str(extracted),
        )

    # 4) Grounding — verify the assembled answer against the documents.
    verdict = client.grounding(
        documents=[req.criteria_text, safe_text],
        question="Is the eligibility answer fully supported by the documents?",
        answer=str(decisions),
        evidence="all",
    )

    return {
        "status": "ok",
        "message": "Live check complete.",
        "extracted": extracted,
        "decisions": decisions,
        "grounding": verdict,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

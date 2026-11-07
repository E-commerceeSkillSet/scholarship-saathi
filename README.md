# Scholarship Saathi

Pakistan scholarship eligibility checker — Honhaar / HEC Need-Based / PEEF.

A student pastes (a) their profile / result-card text and (b) a scholarship
scheme's criteria text. The app answers, per scheme, **ELIGIBLE / LIKELY NOT /
NEEDS CHECK**, with every rule's pass/fail, a probability, and the exact quoted
evidence from the pasted text — plus a missing-info list and a next step.

It never says "you will get the scholarship". It checks only against the
criteria text the user pastes in — that is sample criteria for the demo, not
live official data, and criteria change yearly. **Always check on the official
portal before applying.**

## How Clocked is used

Base: `https://clocked.rezolve.ai/clocked`, Python SDK `clocked-sdk==0.7.0`
(`Clocked(api_key)`), key read from the `CLOCKED_API_KEY` environment variable
on the server only — never in frontend code.

| Step | Endpoint | What it does |
| --- | --- | --- |
| 1 | `pii` | Anonymizes the student text first (`anonymize="replace"`, entities: person, email, phone) so personal data is not sent onward raw. |
| 2 | `extract` | Pulls Matric %, FSc %, domicile, monthly family income, programme and university type out of the profile text — verbatim values with source positions. |
| 3 | `decide` | Asks one `noul` question per scheme rule, with instructions + criteria; returns a typed true/false answer plus a probability per rule. |
| 4 | `grounding` | Verifies the assembled answer against the source documents (`evidence="all"`) and returns a verdict. |

Credits: 1 credit per 25 ms of model time, minimum 1 credit per request. The
UI shows the credits used for each check.

## Run it

```bash
cp .env.example .env        # put your CLOCKED_API_KEY in .env (server only)
pip install -r requirements.txt
python app.py               # serves POST /api/check on port 8000
```

No key? The web demo's **Fixtures mode** uses the pre-recorded responses in
`fixtures/` so anyone can explore the full flow without a key. It is labelled
"demo data — live mode needs a key" in the UI.

## Demo

- Live demo: <!-- TODO: paste the deployed demo link here -->
- Video (30–60s): <!-- TODO: paste the demo video link here --> — script in
  `demo-script.md`.

Built for the Clocked (Rezolve AI) Build Challenge.

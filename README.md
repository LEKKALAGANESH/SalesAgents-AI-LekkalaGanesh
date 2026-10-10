# SalesAgents AI — Home Credit LAP Voice Agent

A prompt-led voice-agent assignment prototype for preliminary Home Credit Loan Against Property (LAP) qualification. The repository contains the system-prompt draft, requirements documentation, and a deterministic Python business-rule API.

## Implemented

- `system-prompt.txt`: platform-neutral prompt template with required runtime placeholders.
- `app/qualification.py`: deterministic in-call state and eligibility rules.
- `app/api.py`: HTTP API for creating sessions and processing structured facts.
- `tests/test_qualification.py`: unit tests for eligibility, terminal outcomes, and boundary cases.
- `docs/`: requirements, architecture, conversation design, test matrix, review, and submission checklist.
- `.github/workflows/tests.yml`: CI workflow for Python unit tests.

## Business rules

| Rule | Behavior |
|---|---|
| Property type | Residential, commercial, industrial allowed; agricultural disqualified |
| Ownership | Sole and joint allowed |
| Original documents | Must be available for verification |
| Loan amount | Maximum ₹75 lakh; higher requests require explicit acceptance of ₹75 lakh |
| Occupation and income | Salaried/self-employed allowed; cash income disqualified |
| Market value | Capture estimate; no minimum threshold specified |
| Tenure | 3–15 years inclusive |
| Existing property loan / EMI reduction | Specialist follow-up branch; end fresh-loan flow |
| Handoff | Only after all seven checklist items pass |

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
uvicorn app.api:app --reload
```

- Health endpoint: `GET /health`
- Interactive API docs: http://127.0.0.1:8000/docs
- Create a session: `POST /sessions` with JSON `{"session_id":"demo-001"}`
- Process a turn: `POST /sessions/demo-001/turn`

Example request body for a fully eligible customer (all monetary values are integer INR):

```json
{
  "facts": {
    "property_type": "residential",
    "ownership_status": "joint",
    "documents_available": true,
    "loan_amount": 5000000,
    "occupation": "self-employed",
    "income_mode": "bank",
    "market_value": 12000000,
    "tenure_years": 10
  }
}
```

Run unit tests:

```bash
python -m unittest discover -s tests -v
```

## Status and limitations

This is a deterministic policy/state service, not a complete deployed voice product. The engine receives structured facts from an upstream voice model/platform; it does not itself extract facts from natural language, place phone calls, or connect to Retell AI. Session state is in-memory only. Authentication, persistent storage, deployment, and a verified Retell adapter remain outstanding.

See [Retell setup and integration notes](docs/retell-setup.md) and [the submission checklist](docs/submission-checklist.md). Do not claim live tests or deployment until verified.

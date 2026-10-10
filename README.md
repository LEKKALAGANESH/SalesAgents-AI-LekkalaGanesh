# SalesAgents AI — Home Credit LAP Voice Agent

A prompt-led voice-agent assignment prototype for preliminary Home Credit Loan Against Property (LAP) qualification. It includes deterministic eligibility rules, a FastAPI service, a secured Retell custom-function endpoint, automated tests, and a Render deployment blueprint.

## Implemented

- `system-prompt.txt`: platform-neutral prompt template with required runtime placeholders.
- `app/qualification.py`: deterministic eligibility rules and conversation state.
- `app/api.py`: session API plus `POST /retell/lap-qualification` custom-function adapter.
- `retell/lap_qualification_function.json`: starting JSON schema for the Retell custom function.
- `render.yaml`: deployment blueprint; configure the generated secrets in the Retell dashboard.
- `tests/`: qualification and API adapter tests.
- `.github/workflows/tests.yml`: CI workflow for Python tests.

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
- Retell custom function endpoint: `POST /retell/lap-qualification`

Copy `.env.example` to `.env` and set a strong `RETELL_WEBHOOK_SECRET` before configuring the Retell endpoint. Set `API_AUTH_TOKEN` before exposing the general session endpoints publicly. Do not commit real secrets. See [Retell setup](docs/retell-setup.md).

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Status and limitations

The code and deployment configuration are committed on the integration feature branch; merge and CI status should be confirmed from the pull request. The adapter accepts **structured facts**, not raw utterances: the configured voice agent must extract facts carefully and omit ambiguous values. Session state is in-memory and resets when the service restarts; run a single instance for the demo and add durable shared storage before production.

A repository change does not deploy the API or configure a Retell account automatically. Live voice tests, recordings, transcripts, and submission evidence remain pending until they are created and verified. See [the test plan](docs/testing.md) and [submission checklist](docs/submission-checklist.md).

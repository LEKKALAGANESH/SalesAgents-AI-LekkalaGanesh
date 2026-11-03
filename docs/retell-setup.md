# Retell AI Setup and Integration Notes

## What the code now provides

- Deterministic eligibility and conversation state in `app/qualification.py`.
- Session endpoints in `app/api.py`.
- `POST /retell/lap-qualification`, a custom-function target that accepts structured facts, calls the qualification engine, and returns a concise next action.
- `retell/lap_qualification_function.json`, a starting schema to configure the Retell custom function.
- Optional API-token protection for the general session endpoints.

The adapter **does not extract facts from raw audio/text, place calls, configure the Retell workspace, or arrange a human transfer by itself**. The agent must extract only explicit facts and follow the returned action. A transfer result is a routing instruction, not a telephony transfer unless a separate transfer workflow is configured.

## 1. Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
uvicorn app.api:app --reload
```

Open http://127.0.0.1:8000/docs and confirm `GET /health` returns `{"status":"ok"}`.

## 2. Configure secrets

Copy `.env.example` to `.env` for local development, then set a long random `RETELL_WEBHOOK_SECRET`. The Retell function must send that exact value as either `Authorization: Bearer <secret>` or `X-Retell-Webhook-Secret: <secret>`.

Before exposing `/sessions` or `/sessions/{session_id}/turn`, also set `API_AUTH_TOKEN`; those endpoints accept it as `X-API-Key` or a Bearer token. Keep both secrets out of Git. `/health` intentionally remains public for hosting health checks.

If using Render, review `render.yaml` and deploy the repository through the Render dashboard. Copy the generated `RETELL_WEBHOOK_SECRET` from the service's environment settings into Retell's secret/header configuration. The exact dashboard steps can change; verify the endpoint is reachable over HTTPS before connecting Retell.

## 3. Configure Retell's custom function

1. Create or open the voice agent in Retell.
2. Paste the approved `system-prompt.txt` content into its instructions.
3. Map runtime placeholders to actual Retell variables using the syntax supported by your selected agent configuration. Do not leave literal placeholders unresolved.
4. Create a custom function named `lap_qualification` using the parameters in [the JSON schema](../retell/lap_qualification_function.json).
5. Set the request URL to `https://<your-deployed-host>/retell/lap-qualification`.
6. Configure the authentication header with the same secret as `RETELL_WEBHOOK_SECRET`. Replace the example placeholder; never store the real secret in the repository.
7. Make sure the function sends a stable `session_id` for every invocation. If it cannot send one, the adapter can use `call.call_id` from the request envelope.
8. Ensure arguments are nested under `args` (or sent directly) and include `facts`. The adapter accepts either shape.
9. Test the function once with a verified customer and one explicit fact. Inspect the response fields: `action`, `message`, `terminal`, `terminal_outcome`, `qualified`, and `missing_fields`.

### Example request

```json
{
  "args": {
    "session_id": "retell-call-demo-001",
    "customer_verified": true,
    "facts": {
      "property_type": "residential",
      "ownership_status": "joint",
      "documents_available": true,
      "loan_amount": 5000000,
      "occupation": "salaried",
      "income_mode": "bank",
      "market_value": 10000000,
      "tenure_years": 10
    }
  }
}
```

The successful response should include `terminal_outcome: "QUALIFIED_FOR_EXPERT_FOLLOWUP"` and `action: "QUALIFIED_HANDOFF_AND_END"`. This is an API behavior example, not evidence of a live Retell call.

## 4. Deploy and connect

A starter Render blueprint is included in `render.yaml`. Deployment requires you to authorize the repository in Render, review any plan/cost settings, create the service, wait for a successful deployment, and copy the generated webhook secret into Retell. This repository integration cannot perform those account-level actions or verify a deployment without access to your hosting and Retell workspaces.

**Demo limitation:** session state currently lives in process memory. Use one running API instance, avoid restarts during a call, and do not treat this setup as production-ready. Durable shared storage, rate limiting, monitoring, and a tested recovery strategy are still required before production use.

## 5. Run tests

```bash
python -m unittest discover -s tests -v
```

The API adapter tests cover secret rejection, the eligible path, transfer routing, and invalid facts. Automated tests cannot prove speech extraction accuracy, prompt adherence, live call behavior, or that Retell is configured correctly.

## 6. End-to-end test checklist

- [ ] The agent verifies the intended customer before disclosing offer details.
- [ ] A complete eligible call returns the qualified expert follow-up outcome only after all seven checklist items are complete.
- [ ] Agricultural property, unavailable originals, cash income, and tenure outside 3–15 years disqualify immediately.
- [ ] Above-cap loan requests require explicit agreement to ₹75 lakh; decline ends the call.
- [ ] Existing property loan and EMI-reduction cases route to specialist follow-up.
- [ ] Busy customer gets a callback question and the current call ends.
- [ ] Corrections, interruptions, ambiguity, and multiple facts in one utterance are handled safely.
- [ ] Exact interest rates and unprovided product details are never invented.
- [ ] Recordings, transcripts, and call logs are saved with privacy-safe sharing permissions.

Record actual results in [testing.md](testing.md). Do not mark a scenario passed until a real run has been reviewed.

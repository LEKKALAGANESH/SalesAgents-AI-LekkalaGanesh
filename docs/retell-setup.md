# Retell AI Setup and Integration Notes

## Current implementation boundary

This repository contains a deterministic Python qualification engine and HTTP API. It does **not** place calls, manage phone numbers, or connect to Retell automatically. A configured Retell agent and credentials are required before a platform integration can be verified.

The API accepts structured facts extracted from the conversation. Use the system prompt to extract facts and drive dialogue; use this service as a policy/state check. Do not claim a call was placed or an agent deployed until verified in the Retell workspace.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

python -m pip install -r requirements.txt
uvicorn app.api:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API docs and http://127.0.0.1:8000/health for the health check.

## API sequence

1. Create a session with `POST /sessions` and JSON `{"session_id":"demo-001"}`.
2. Verify the customer using `POST /sessions/demo-001/turn` with `{"customer_verified":true}`.
3. Send structured facts to the same turn endpoint. Example:

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

Amounts and property values are integer INR. `documents_available` must be a boolean. Omit unclear facts instead of guessing. A correction is sent as a later fact value and replaces the earlier value.

## Retell configuration checklist

1. Create a Retell AI account and a new voice agent in the Retell dashboard.
2. Paste the approved contents of [system-prompt.txt](../system-prompt.txt) into the agent instructions.
3. Map every runtime variable (company, customer, agent identity/gender, date/time, RAG context, language, conversation history, latest utterance) using Retell's supported template syntax.
4. Set the agent language and professional voice. Verify English/Hindi behavior and configured agent gender in test calls.
5. Decide whether the deterministic API will be invoked through a supported custom function or a webhook adapter. Map the platform's event/function schema to `/sessions` and `/sessions/{session_id}/turn`. Do not send raw, unvalidated customer text as trusted structured facts.
6. Keep API credentials in the platform's secret manager or environment, never in source control.
7. Run the scenarios in [testing.md](testing.md), record observed results, and save call audio, transcripts, and call logs.
8. Verify that the evidence link can be opened by the evaluator.

## Important limitations

- Session state is in-process memory. It resets on service restart and is not shared across multiple workers. Use durable storage and access controls before production.
- The API does not include authentication, rate limiting, telephony, speech recognition, or an LLM fact extractor. Do not expose it publicly without authentication and deployment hardening.
- The engine returns an action and guidance message; the voice platform remains responsible for speaking naturally, ending the call, scheduling callbacks, and arranging human follow-up.
- Static unit tests validate deterministic business rules only. They do not prove speech recognition, prompt behavior, Retell integration, or live-call success.

"""HTTP API and Retell custom-function adapter for the LAP qualification engine.

The Retell endpoint consumes structured, already-extracted facts. It does not
perform speech-to-text or infer facts from raw utterances.
"""
from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.qualification import QualificationEngine

app = FastAPI(
    title="SalesAgents AI — LAP Qualification API",
    version="0.2.0",
    description="Deterministic eligibility and conversation-state service for the Home Credit LAP assignment.",
)
engine = QualificationEngine()


class CreateSessionRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)


class TurnRequest(BaseModel):
    facts: dict[str, Any] = Field(default_factory=dict)
    customer_verified: bool | None = None
    customer_busy: bool = False
    callback_time: str | None = None
    existing_property_loan: bool = False
    emi_reduction_request: bool = False
    accept_maximum: bool | None = None
    customer_declines: bool = False


def _check_secret(provided: str | None, expected: str, label: str) -> None:
    if not provided or not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail=f"Invalid {label}.")


def require_api_token(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> None:
    """Require a token when API_AUTH_TOKEN is configured; leave local dev easy."""
    expected = os.getenv("API_AUTH_TOKEN")
    if not expected:
        return
    bearer = authorization.removeprefix("Bearer ").strip() if authorization else None
    _check_secret(x_api_key or bearer, expected, "API token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "lap-qualification-api"}


@app.post("/sessions", status_code=201, dependencies=[Depends(require_api_token)])
def create_session(request: CreateSessionRequest) -> dict[str, Any]:
    try:
        state = engine.create_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return state.to_dict()


@app.get("/sessions/{session_id}", dependencies=[Depends(require_api_token)])
def get_session(session_id: str) -> dict[str, Any]:
    try:
        return engine.get_session(session_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/sessions/{session_id}/turn", dependencies=[Depends(require_api_token)])
def process_turn(session_id: str, request: TurnRequest) -> dict[str, Any]:
    try:
        state = engine.process_turn(
            session_id,
            facts=request.facts,
            customer_verified=request.customer_verified,
            customer_busy=request.customer_busy,
            callback_time=request.callback_time,
            existing_property_loan=request.existing_property_loan,
            emi_reduction_request=request.emi_reduction_request,
            accept_maximum=request.accept_maximum,
            customer_declines=request.customer_declines,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return state.to_dict()


@app.post("/retell/lap-qualification")
async def retell_lap_qualification(
    request: Request,
    authorization: str | None = Header(default=None),
    x_retell_webhook_secret: str | None = Header(default=None, alias="X-Retell-Webhook-Secret"),
) -> dict[str, Any]:
    """Retell custom-function target.

    Accepts either direct arguments or a Retell-style {"args": {...}} envelope.
    Configure RETELL_WEBHOOK_SECRET before exposing this endpoint.
    """
    expected = os.getenv("RETELL_WEBHOOK_SECRET")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Retell adapter is disabled until RETELL_WEBHOOK_SECRET is configured.",
        )
    bearer = authorization.removeprefix("Bearer ").strip() if authorization else None
    _check_secret(x_retell_webhook_secret or bearer, expected, "Retell webhook secret")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="Request body must be a JSON object.")

    args = payload.get("args", payload.get("arguments", payload))
    if not isinstance(args, dict):
        raise HTTPException(status_code=422, detail="Function arguments must be a JSON object.")

    call = payload.get("call") if isinstance(payload.get("call"), dict) else {}
    session_id = args.get("session_id") or payload.get("session_id") or call.get("call_id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Provide session_id or a Retell call.call_id to identify the conversation.",
        )
    session_id = session_id.strip()[:128]

    try:
        engine.get_session(session_id)
    except KeyError:
        try:
            engine.create_session(session_id)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    try:
        turn = TurnRequest.model_validate(args)
        state = engine.process_turn(
            session_id,
            facts=turn.facts,
            customer_verified=turn.customer_verified,
            customer_busy=turn.customer_busy,
            callback_time=turn.callback_time,
            existing_property_loan=turn.existing_property_loan,
            emi_reduction_request=turn.emi_reduction_request,
            accept_maximum=turn.accept_maximum,
            customer_declines=turn.customer_declines,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Keep the return payload short and predictable for the voice agent.
    return {
        "session_id": state.session_id,
        "action": state.last_action,
        "message": state.last_message,
        "terminal": state.terminal,
        "terminal_outcome": state.terminal_outcome,
        "qualified": state.qualified,
        "awaiting_maximum_acceptance": state.awaiting_maximum_acceptance,
        "missing_fields": _missing_fields(state.to_dict()),
    }


def _missing_fields(state: dict[str, Any]) -> list[str]:
    checks = {
        "property_type": state.get("property_type"),
        "ownership_status": state.get("ownership_status"),
        "documents_available": state.get("documents_available"),
        "loan_amount": state.get("loan_amount"),
        "occupation": state.get("occupation"),
        "income_mode": state.get("income_mode"),
        "market_value": state.get("market_value"),
        "tenure_years": state.get("tenure_years"),
    }
    return [name for name, value in checks.items() if value is None]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )

"""HTTP API for a voice-platform adapter.

The endpoint accepts structured facts extracted from a customer utterance. This
service does not call Retell or place phone calls by itself.
"""
from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.qualification import QualificationEngine

app = FastAPI(
    title="SalesAgents AI — LAP Qualification API",
    version="0.1.0",
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "lap-qualification-api"}


@app.post("/sessions", status_code=201)
def create_session(request: CreateSessionRequest) -> dict[str, Any]:
    try:
        state = engine.create_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return state.to_dict()


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    try:
        return engine.get_session(session_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/sessions/{session_id}/turn")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )

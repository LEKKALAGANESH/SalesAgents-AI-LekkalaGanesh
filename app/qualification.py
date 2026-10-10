"""Deterministic business-rule engine for the Home Credit LAP assignment.

This module consumes structured facts extracted by the voice model. It does not
pretend to be a reliable natural-language parser: the voice prompt/platform
extracts facts; this engine validates policy and chooses the next action.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

MAX_LOAN_AMOUNT = 7_500_000
MIN_TENURE_YEARS = 3
MAX_TENURE_YEARS = 15

CHECKLIST = (
    ("property_type", "What type of property would you like to use: residential, commercial, or industrial?"),
    ("ownership_status", "Is the property solely owned by you, or is it jointly owned?"),
    ("documents_available", "Are the original property documents available for verification?"),
    ("loan_amount", "Approximately how much would you like to borrow?"),
    ("occupation_and_income", "Are you salaried or self-employed, and is your income received through a bank or in cash?"),
    ("market_value", "Approximately what is the current market value of the property?"),
    ("tenure_years", "Over how many years would you like to repay the loan?"),
)

TERMINAL_OUTCOMES = {
    "CALLBACK_REQUESTED", "TRANSFER_SPECIALIST_FOLLOWUP", "DISQUALIFIED",
    "CUSTOMER_DECLINED_MAXIMUM", "WRONG_CUSTOMER", "QUALIFIED_FOR_EXPERT_FOLLOWUP",
}


@dataclass
class QualificationState:
    session_id: str
    customer_verified: bool | None = None
    customer_available: bool | None = None
    callback_time: str | None = None
    property_type: str | None = None
    ownership_status: str | None = None
    documents_available: bool | None = None
    loan_amount: int | None = None
    requested_loan_amount: int | None = None
    occupation: str | None = None
    income_mode: str | None = None
    market_value: int | None = None
    tenure_years: int | None = None
    existing_property_loan: bool = False
    emi_reduction_request: bool = False
    awaiting_maximum_acceptance: bool = False
    disqualified: bool = False
    transfer_required: bool = False
    qualified: bool = False
    terminal_outcome: str | None = None
    last_action: str = "VERIFY_CUSTOMER"
    last_message: str = "Greet the customer and verify that you are speaking with the intended person."
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def terminal(self) -> bool:
        return self.terminal_outcome in TERMINAL_OUTCOMES

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["terminal"] = self.terminal
        return result


class QualificationEngine:
    """Applies eligibility policy to a single in-memory qualification session."""

    def __init__(self) -> None:
        self._sessions: dict[str, QualificationState] = {}

    def create_session(self, session_id: str) -> QualificationState:
        if not session_id or not session_id.strip():
            raise ValueError("session_id must be a non-empty string")
        if session_id in self._sessions:
            raise ValueError(f"session {session_id!r} already exists")
        state = QualificationState(session_id=session_id)
        self._sessions[session_id] = state
        return state

    def get_session(self, session_id: str) -> QualificationState:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Unknown session: {session_id}") from exc

    def process_turn(
        self,
        session_id: str,
        *,
        facts: Mapping[str, Any] | None = None,
        customer_verified: bool | None = None,
        customer_busy: bool = False,
        callback_time: str | None = None,
        existing_property_loan: bool = False,
        emi_reduction_request: bool = False,
        accept_maximum: bool | None = None,
        customer_declines: bool = False,
    ) -> QualificationState:
        state = self.get_session(session_id)
        if state.terminal:
            return state

        facts = dict(facts or {})
        self._validate_fact_keys(facts)

        # Capture all explicit facts, including facts volunteered out of order.
        if customer_verified is not None:
            state.customer_verified = customer_verified
        if "customer_verified" in facts:
            if not isinstance(facts["customer_verified"], bool):
                raise ValueError("customer_verified must be a boolean")
            state.customer_verified = facts["customer_verified"]

        self._apply_facts(state, facts)
        state.existing_property_loan = state.existing_property_loan or existing_property_loan
        state.emi_reduction_request = state.emi_reduction_request or emi_reduction_request
        state.events.append({"type": "turn_processed", "facts": facts})

        if state.customer_verified is False:
            return self._finish(
                state, "WRONG_CUSTOMER", "END_CALL",
                "Apologize briefly, do not reveal offer details, and end the call.",
            )

        if state.customer_verified is not True:
            state.last_action = "VERIFY_CUSTOMER"
            state.last_message = "Ask to speak with the intended customer; do not reveal offer details yet."
            return state

        if customer_busy:
            state.customer_available = False
            state.callback_time = callback_time.strip() if callback_time else None
            return self._finish(
                state, "CALLBACK_REQUESTED", "ASK_CALLBACK_AND_END",
                "Ask for a convenient callback time, acknowledge it, and end the current call.",
            )

        state.customer_available = True

        # Explicit precedence: a confirmed existing-loan/EMI-reduction case is an
        # alternate workflow, not fresh-loan qualification. Route it to a specialist.
        if state.existing_property_loan or state.emi_reduction_request:
            state.transfer_required = True
            return self._finish(
                state, "TRANSFER_SPECIALIST_FOLLOWUP", "TRANSFER_SPECIALIST_AND_END",
                "Explain that a loan-transfer specialist will contact the customer, then end the call.",
            )

        disqualifier = self._first_disqualifier(state)
        if disqualifier:
            state.disqualified = True
            return self._finish(
                state, "DISQUALIFIED", "EXPLAIN_INELIGIBILITY_AND_END",
                "Politely explain that the customer does not meet this offer's criteria and end the call.",
                reason=disqualifier,
            )

        if state.awaiting_maximum_acceptance:
            if accept_maximum is True:
                state.loan_amount = MAX_LOAN_AMOUNT
                state.requested_loan_amount = MAX_LOAN_AMOUNT
                state.awaiting_maximum_acceptance = False
            elif accept_maximum is False or customer_declines:
                return self._finish(
                    state, "CUSTOMER_DECLINED_MAXIMUM", "THANK_AND_END",
                    "Thank the customer and end the call because they declined the ₹75 lakh alternative.",
                )
            else:
                state.last_action = "CONFIRM_MAXIMUM_AMOUNT"
                state.last_message = "Explain the ₹75 lakh limit and ask whether the customer wants to proceed with ₹75 lakh."
                return state

        if state.loan_amount is not None and state.loan_amount > MAX_LOAN_AMOUNT:
            state.requested_loan_amount = state.loan_amount
            state.awaiting_maximum_acceptance = True
            state.last_action = "CONFIRM_MAXIMUM_AMOUNT"
            state.last_message = "Explain the ₹75 lakh limit and ask whether the customer wants to proceed with ₹75 lakh."
            return state

        if customer_declines:
            return self._finish(
                state, "CUSTOMER_DECLINED_MAXIMUM", "THANK_AND_END",
                "Thank the customer and end the call.",
            )

        missing = self._first_missing_item(state)
        if missing:
            state.last_action = "ASK_NEXT_QUESTION"
            state.last_message = missing[1]
            return state

        state.qualified = True
        return self._finish(
            state, "QUALIFIED_FOR_EXPERT_FOLLOWUP", "QUALIFIED_HANDOFF_AND_END",
            "Tell the customer a senior loan expert will contact them about next steps and the exact interest rate; do not promise approval.",
        )

    @staticmethod
    def _validate_fact_keys(facts: Mapping[str, Any]) -> None:
        allowed = {
            "customer_verified", "property_type", "ownership_status",
            "documents_available", "loan_amount", "occupation", "income_mode",
            "market_value", "tenure_years",
        }
        unknown = set(facts) - allowed
        if unknown:
            raise ValueError(f"Unsupported fact field(s): {', '.join(sorted(unknown))}")

    @staticmethod
    def _apply_facts(state: QualificationState, facts: Mapping[str, Any]) -> None:
        if "property_type" in facts:
            state.property_type = QualificationEngine._choice(
                facts["property_type"], {"residential", "commercial", "industrial", "agricultural"}
            )
        if "ownership_status" in facts:
            state.ownership_status = QualificationEngine._choice(
                facts["ownership_status"], {"sole", "joint"}
            )
        if "documents_available" in facts:
            value = facts["documents_available"]
            if not isinstance(value, bool):
                raise ValueError("documents_available must be true or false; omit it when ambiguous")
            state.documents_available = value
        if "loan_amount" in facts:
            amount = facts["loan_amount"]
            if amount is not None and (not isinstance(amount, int) or isinstance(amount, bool) or amount < 0):
                raise ValueError("loan_amount must be a non-negative integer in INR")
            if amount is not None:
                state.loan_amount = amount
                state.requested_loan_amount = amount
        if "occupation" in facts:
            state.occupation = QualificationEngine._choice(facts["occupation"], {"salaried", "self-employed"})
        if "income_mode" in facts:
            state.income_mode = QualificationEngine._choice(facts["income_mode"], {"bank", "cash"})
        if "market_value" in facts:
            value = facts["market_value"]
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
                raise ValueError("market_value must be a non-negative integer in INR")
            state.market_value = value
        if "tenure_years" in facts:
            years = facts["tenure_years"]
            if years is not None and (not isinstance(years, int) or isinstance(years, bool)):
                raise ValueError("tenure_years must be an integer")
            state.tenure_years = years

    @staticmethod
    def _choice(value: Any, allowed: set[str]) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip().lower().replace("_", "-")
        aliases = {
            "residential property": "residential",
            "commercial property": "commercial",
            "industrial property": "industrial",
            "agricultural land": "agricultural",
            "sole ownership": "sole",
            "solely owned": "sole",
            "single": "sole",
            "joint ownership": "joint",
            "jointly owned": "joint",
            "self employed": "self-employed",
            "self-employment": "self-employed",
            "bank account": "bank",
            "cash income": "cash",
        }
        normalized = aliases.get(normalized, normalized)
        if normalized not in allowed:
            raise ValueError(f"Unsupported value {value!r}; expected one of {sorted(allowed)}")
        return normalized

    @staticmethod
    def _first_disqualifier(state: QualificationState) -> str | None:
        if state.property_type == "agricultural":
            return "AGRICULTURAL_PROPERTY"
        if state.documents_available is False:
            return "ORIGINAL_DOCUMENTS_UNAVAILABLE"
        if state.income_mode == "cash":
            return "CASH_INCOME"
        if state.tenure_years is not None and not MIN_TENURE_YEARS <= state.tenure_years <= MAX_TENURE_YEARS:
            return "TENURE_OUT_OF_RANGE"
        return None

    @staticmethod
    def _first_missing_item(state: QualificationState) -> tuple[str, str] | None:
        checks = [
            (state.property_type is not None, CHECKLIST[0]),
            (state.ownership_status is not None, CHECKLIST[1]),
            (state.documents_available is not None, CHECKLIST[2]),
            (state.loan_amount is not None, CHECKLIST[3]),
            (state.occupation is not None and state.income_mode is not None, CHECKLIST[4]),
            (state.market_value is not None, CHECKLIST[5]),
            (state.tenure_years is not None, CHECKLIST[6]),
        ]
        for complete, item in checks:
            if not complete:
                return item
        return None

    @staticmethod
    def _finish(
        state: QualificationState,
        outcome: str,
        action: str,
        message: str,
        **metadata: Any,
    ) -> QualificationState:
        state.terminal_outcome = outcome
        state.last_action = action
        state.last_message = message
        state.events.append({"type": "terminal_outcome", "outcome": outcome, **metadata})
        return state

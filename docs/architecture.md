# Proposed Architecture

> This is a proposed logical architecture for the assignment, not a claim about an already implemented system. The selected voice platform and its capabilities remain to be confirmed.

## 1. Logical components

```text
Telephony / Voice Platform
          |
          v
Conversation Orchestrator
          |
          +--> Prompt Template + Runtime Variables
          |
          +--> In-call Qualification State
          |       - verification / availability
          |       - seven checklist items
          |       - transfer / disqualification flags
          |
          +--> Business-rule evaluation
          |
          +--> Approved Context (additional_context_from_rag)
          |
          +--> Outcome routing
                  - callback
                  - transfer specialist
                  - disqualification
                  - qualified-lead follow-up
          |
          v
Call transcript / logs / recording evidence
```

The implementation may collapse some components into features provided by the voice platform. Any behavior that depends on external tooling should be verified against the chosen platform.

## 2. Responsibilities

### Voice platform
- Handle the inbound/outbound audio session and turn-taking.
- Provide the current customer utterance and conversation history where supported.
- Apply the configured prompt and voice settings.
- Expose call transcripts, recordings, and logs for evaluation.

### Conversation orchestrator
- Apply the prompt and track the current conversation stage.
- Extract any facts the customer provided, including facts volunteered out of order.
- Determine the earliest unanswered checklist item.
- Avoid moving to a terminal outcome twice or continuing after a terminal outcome.

### Qualification state
Proposed per-call fields:

| Field | Initial value | Notes |
|---|---|---|
| `customer_verified` | `UNKNOWN` | Must be established before the offer |
| `customer_available` | `UNKNOWN` | Busy flow ends with callback time |
| `property_type` | `UNKNOWN` | Residential / Commercial / Industrial / Agricultural |
| `ownership_status` | `UNKNOWN` | Sole / Joint |
| `documents_available` | `UNKNOWN` | Original documents available for verification |
| `loan_amount` | `UNKNOWN` | If > ₹75 lakh, negotiate down to ₹75 lakh |
| `occupation` | `UNKNOWN` | Salaried / Self-employed |
| `income_mode` | `UNKNOWN` | Bank / Cash |
| `market_value` | `UNKNOWN` | Customer estimate; no threshold specified |
| `tenure_years` | `UNKNOWN` | 3–15 inclusive |
| `existing_property_loan` | `UNKNOWN` | Positive detection activates transfer branch |
| `emi_reduction_request` | `UNKNOWN` | Positive detection activates transfer branch |
| `callback_time` | `UNKNOWN` | Required when customer is busy |
| `disqualified` | `FALSE` | Terminal decision flag |
| `transfer_required` | `FALSE` | Terminal decision flag |
| `qualified` | `FALSE` | True only after complete successful checklist |

Use a distinct unknown/not-yet-captured value; do not interpret missing values as false or eligible.

## 3. Core response algorithm

For each customer utterance:

1. **Extract** all clear facts, intent signals, and corrections from the utterance.
2. **Update** the qualification state; the latest clear correction replaces an older value.
3. **Route existing-loan/EMI-reduction cases** to the transfer-specialist message and end.
4. **Validate eligibility**; if a disqualifying fact is clear, explain and end immediately.
5. **Handle availability/diversion/interruption** using the relevant conversation rule.
6. **Find the first missing checklist item** in the defined order and ask only that item.
7. If all seven items are known and pass, **handoff** to senior-loan-expert follow-up.

A platform implementation should use deterministic code or structured actions for critical routing where available rather than relying only on a language model to remember terminal decisions.

## 4. End states

- `CALLBACK_REQUESTED`: customer is busy; callback preference captured; current call ended.
- `TRANSFER_SPECIALIST_FOLLOWUP`: existing property loan or EMI-reduction intent; specialist follow-up communicated; current call ended.
- `DISQUALIFIED`: a mandatory eligibility rule failed; polite explanation delivered; call ended.
- `CUSTOMER_DECLINED_MAXIMUM`: customer declined to proceed with ₹75 lakh after requesting more; call ended.
- `QUALIFIED_FOR_EXPERT_FOLLOWUP`: all seven checklist items captured, rules passed, no transfer condition; expert follow-up communicated.
- `CALL_COMPLETED_OTHER`: a platform-supported call end not covered above (e.g., customer declines to continue). Exact handling should be configured consistently.

## 5. Knowledge and RAG boundary

Use `additional_context_from_rag` only as approved product/context input. The agent must not invent exact rates, branch data, or policies missing from that context. The expert provides exact interest rates after preliminary qualification, per the assignment.

## 6. Observability and data handling

**Proposed:** retain outcome, test scenario ID, transcript, and recording reference for evaluation. Avoid storing unnecessary personal information. Recording consent, access control, retention duration, redaction, and production security are open implementation decisions and must be confirmed before real customer use.

# System Prompt Design Guide

This document defines the required prompt sections and behavioral contract. Keep the final deployable system prompt in a separate versioned artifact when the prompt is authored.

## 1. Runtime variables

The prompt must support and correctly use:

- `{{company_name}}`
- `{{customer_name}}`
- `{{agent_name}}`
- `{{agent_gender}}`
- `{{current_date}}`
- `{{current_day}}`
- `{{current_time}}`
- `{{additional_context_from_rag}}`
- `{{language_to_speak}}`
- `{{conversation_history}}`
- `{{customer_utterance}}`

Use the exact placeholder syntax required by the chosen platform; the double-brace form above is illustrative if the platform uses a different templating convention.

## 2. Recommended prompt section order

1. Role and objective.
2. Identity and runtime context.
3. Language, voice, and gender.
4. Conversation principles.
5. Call flow and customer verification.
6. Busy-customer callback behavior.
7. Offer presentation.
8. Existing-loan / EMI-reduction transfer branch.
9. Internal qualification state.
10. Seven checklist items.
11. Explicit eligibility rules.
12. Out-of-order fact capture.
13. Immediate disqualification.
14. Loan amount above ₹75 lakh.
15. Diversion and interruption handling.
16. Approved RAG context behavior.
17. Handoff gate.
18. Call termination rules.
19. Edge cases and examples.

## 3. Core state-management algorithm

The prompt should instruct the agent to apply this algorithm after every customer response:

```text
extract all clear facts and intent signals
apply explicit corrections (latest clear answer wins)
update the qualification state

if existing property loan OR EMI-reduction request:
    explain specialist follow-up
    end call

if any mandatory eligibility criterion clearly fails:
    explain offer-specific ineligibility
    end call

if customer is busy at opening:
    ask for callback time
    capture time
    end call

resolve customer interruption or diversion using approved facts only

find the earliest unanswered checklist item
if one exists:
    ask only that item
else if all seven answers are valid and all criteria pass:
    inform customer of senior expert follow-up
    end call
```

If amount exceeds ₹75 lakh, use the dedicated alternative-offer flow before treating the amount as accepted.

## 4. In-call state fields

At minimum, track:

```text
customer_verified = UNKNOWN
customer_available = UNKNOWN
property_type = UNKNOWN
ownership_status = UNKNOWN
documents_available = UNKNOWN
loan_amount = UNKNOWN
occupation = UNKNOWN
income_mode = UNKNOWN
market_value = UNKNOWN
tenure_years = UNKNOWN
existing_property_loan = UNKNOWN
emi_reduction_request = UNKNOWN
callback_time = UNKNOWN
disqualified = FALSE
transfer_required = FALSE
qualified = FALSE
```

Do not tell the customer about the internal state. Do not treat unknown values as passing criteria.

## 5. Critical policy clauses

- Residential, commercial, and industrial property types are allowed; agricultural property is disqualifying.
- Sole and joint ownership are both allowed.
- Original property documents must be available for verification.
- Maximum offered loan amount is ₹75 lakh. For a greater request, ask whether the customer wants to proceed with ₹75 lakh.
- Salaried and self-employed customers are accepted only when income is received through a bank; cash income is disqualifying.
- Capture market value without adding a minimum-value threshold.
- Tenure must be 3–15 years inclusive.
- Existing property loan or EMI reduction triggers specialist follow-up and ends the fresh-loan flow.
- Only hand off after all seven checklist items are answered and all applicable criteria pass.
- Do not invent exact rates or unsupported product facts.

## 6. Voice behavior

- Use short, natural turns.
- Understand conversational phrasing rather than requiring yes/no answers.
- Capture several facts from a single utterance.
- Pause for customer questions, answer within approved knowledge, and resume at the earliest unanswered item.
- Clarify ambiguous facts.
- Keep configured language and agent gender consistent.
- Do not claim final approval.

## 7. Prompt review checklist

- [ ] All required variables are used where relevant.
- [ ] The call flow starts with identity verification and availability.
- [ ] Busy customers receive a callback question and the current call ends.
- [ ] Transfer and disqualification branches are terminal.
- [ ] Out-of-order facts are captured without repeated questions.
- [ ] Loan-amount cap negotiation is explicit.
- [ ] All seven checklist items gate handoff.
- [ ] Unknown context never results in fabricated facts.
- [ ] No unsupported eligibility rules appear.
- [ ] Edge cases map to executable test scenarios in [testing.md](testing.md).

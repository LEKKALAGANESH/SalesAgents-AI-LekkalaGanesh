# Product Requirements Document (PRD)

## 1. Summary

Build an AI voice agent for Home Credit that contacts existing customers, presents a special Loan Against Property (LAP) offer of up to ₹75,00,000, gathers seven eligibility checklist items, applies the stated business rules, and routes the outcome appropriately.

The agent is a preliminary qualification assistant, not the final loan decision-maker. Customers who pass the checks are told that a senior loan expert will call back to discuss next steps and provide the exact interest rate.

## 2. Problem and outcome

The business needs a consistent first-contact experience that can qualify leads naturally while correctly handling ineligible cases, existing-property-loan/EMI-reduction cases, interruptions, diversions, and customers who provide details out of sequence.

**Desired outcome:** every call ends in a clear, policy-consistent outcome: callback scheduled, transfer-specialist follow-up, disqualification, or qualified-lead handoff.

## 3. Primary user and stakeholders

- **Customer:** an existing Home Credit customer contacted about the LAP offer.
- **AI voice agent:** verifies identity, explains the offer, captures the required details, and follows the decision logic.
- **Senior loan expert:** follows up with leads that pass all seven checklist items and provides details such as the exact interest rate.
- **Loan-transfer specialist:** follows up when the customer has an existing loan on the property or wants to reduce an existing EMI.
- **Project evaluator / developer:** configures the prompt, runs tests, and prepares submission evidence.

## 4. Goals

1. Verify that the agent is speaking with the intended customer.
2. Ask whether the customer is available; capture a convenient callback time if not.
3. Explain the offer in a professional, advisory, non-robotic manner.
4. Detect existing-loan and EMI-reduction cases before continuing fresh-loan qualification.
5. Capture all seven checklist items while reusing facts supplied out of order.
6. Enforce eligibility rules and immediately end the standard flow after a disqualifying answer.
7. Offer the ₹75 lakh maximum alternative when a customer requests more than ₹75 lakh.
8. Hand off only after all seven checklist items are answered and all applicable rules pass.
9. Demonstrate behavior with multiple test calls, transcripts, and recordings.

## 5. Non-goals

- Making the final credit or underwriting decision.
- Promising loan approval or guaranteed disbursal.
- Quoting an exact interest rate when it is not present in approved knowledge.
- Inventing a minimum property-market-value threshold.
- Continuing the fresh-loan checklist for an existing-loan/EMI-reduction case.
- Replacing required test evidence with an untested prompt-only submission.

## 6. Functional requirements

### FR-01 — Identity and availability
- The agent MUST check that it is speaking with the intended customer.
- If the customer asks who is calling, the agent SHOULD identify itself and explain the reason for the call without revealing unnecessary sensitive information.
- If the customer is busy, the agent MUST ask for a convenient callback time and then end the current call without presenting the offer or continuing qualification.

### FR-02 — Offer presentation
- After successful verification and availability, the agent MUST explain that the call concerns a special LAP offer of up to ₹75 lakh, presented as recognition of the customer's loyalty.
- The agent MUST describe this as a preliminary check and MUST NOT imply that final approval is guaranteed.

### FR-03 — Fresh-loan versus transfer routing
- The agent MUST detect whether the customer already has a loan on the property or wants to reduce an existing EMI.
- If either is true, the agent MUST explain that a loan-transfer specialist will contact them shortly and then end the call.
- The agent MUST NOT continue the seven-item fresh-loan checklist in this branch.

### FR-04 — Eligibility checklist
The agent MUST capture these seven checklist items:
1. Property type.
2. Ownership status.
3. Original property-document availability.
4. Desired loan amount.
5. Occupation and income mode (treated as one checklist item).
6. Estimated current property market value.
7. Desired repayment tenure.

The checklist is sequential, but facts already volunteered by the customer MUST be captured and MUST NOT be requested again when clear.

### FR-05 — Eligibility and disqualification
- Agricultural property: disqualify.
- Original documents unavailable: disqualify.
- Income received in cash: disqualify.
- Requested loan amount above ₹75 lakh: offer the ₹75 lakh alternative; do not reject immediately.
- Tenure outside 3–15 years: disqualify.
- Sole and joint ownership are both acceptable.
- Salaried and self-employed occupations are both acceptable when income is received through a bank.
- Record the estimated market value; the assignment specifies no minimum threshold.

### FR-06 — Natural conversation
The agent MUST understand natural sentences, fillers, corrections, interruptions, and multiple facts in one response. When a customer corrects a prior answer, the latest clear answer MUST replace the previous value. Ambiguous eligibility facts MUST be clarified instead of guessed.

### FR-07 — Diversions and product questions
- The agent MUST answer briefly when reliable information is available in approved injected context.
- It MUST NOT fabricate product details, rates, branch locations, or other facts.
- When exact interest rates are not available, it should say that the senior loan expert will provide them after preliminary qualification.
- After resolving a diversion, return to the earliest unanswered checklist item.

### FR-08 — Handoff gate
The agent MUST NOT announce successful preliminary qualification or trigger the qualified-lead handoff until all seven checklist items are answered, all applicable criteria pass, and no transfer condition applies.

### FR-09 — Configurable prompt variables
The system prompt MUST support the assignment's variables:
`company_name`, `customer_name`, `agent_name`, `agent_gender`, `current_date`, `current_day`, `current_time`, `additional_context_from_rag`, `language_to_speak`, `conversation_history`, and `customer_utterance`.

## 7. Non-functional requirements

- **Conversational quality:** short, clear, professional voice turns.
- **Consistency:** deterministic enforcement of explicit business rules.
- **State fidelity:** previously supplied, unambiguous facts are retained within the call.
- **Grounded answers:** use approved context; do not invent missing details.
- **Auditability:** retain test transcripts and call recordings/logs for submission, subject to platform and data-handling rules.
- **Language consistency:** use the configured language (English or Hindi) and maintain the configured agent gender in gendered language.

## 8. Acceptance criteria

- [ ] Customer verification occurs before the offer.
- [ ] Busy customer is asked for a callback time and the call ends.
- [ ] Existing property loan or EMI-reduction intent triggers specialist follow-up and call termination.
- [ ] All seven checklist items are captured before qualified handoff.
- [ ] Out-of-order facts are stored and not re-asked.
- [ ] Agricultural property, unavailable originals, cash income, and out-of-range tenure are handled as disqualifying cases.
- [ ] A request above ₹75 lakh triggers an offer to continue at ₹75 lakh.
- [ ] Joint ownership is not incorrectly rejected.
- [ ] No minimum market-value rule is invented.
- [ ] Unknown interest rates or unrelated facts are not fabricated.
- [ ] Test evidence covers happy paths, failure paths, diversions, interruptions, and corrections.
- [ ] Final submission includes system prompt and a public link to the recording and call logs (audio and transcript).

## 9. Open decisions

These points are not specified by the assignment and should be confirmed before production use:
- Which voice platform will host the agent.
- The mechanism for actual human routing versus telling the customer that a specialist will call.
- Approved privacy, consent, retention, and access controls for recordings and lead data.
- Whether the platform provides structured state/tools in addition to prompt-only state handling.

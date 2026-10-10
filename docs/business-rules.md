# Business Rules and Eligibility Policy

This document is the compact reference for implementing qualification decisions. Rules are derived from the supplied Voice Agent Design assignment.

## 1. Qualification checklist

| # | Checklist item | Accepted values / handling |
|---|---|---|
| 1 | Property type | Residential, Commercial, Industrial: continue. Agricultural: immediate disqualification. |
| 2 | Ownership status | Sole or Joint: continue. |
| 3 | Original-document availability | Original property documents must be available for verification. If unavailable: immediate disqualification. |
| 4 | Desired loan amount | Up to ₹75,00,000: continue. Above ₹75,00,000: explain limit and ask whether customer wants to proceed at ₹75,00,000. |
| 5 | Occupation + income mode | Salaried or Self-employed are acceptable; income must be received through a bank. Cash income: immediate disqualification. |
| 6 | Estimated property market value | Capture customer estimate. No minimum threshold is specified. Do not invent one. |
| 7 | Desired tenure | 3 through 15 years inclusive: continue. Below 3 or above 15: immediate disqualification. |

## 2. Rule precedence

After every customer utterance, apply this order:

1. Extract all clear facts, corrections, and intent signals from the utterance.
2. Update the in-call qualification state with those facts.
3. Check whether the customer has an existing loan on the property or wants to reduce an existing EMI. If yes, take the transfer-specialist branch and end the call.
4. Check for a clearly established disqualifying eligibility answer. If one exists, politely explain that the customer does not meet the criteria for this specific offer at this time and end the call.
5. If the customer is busy at the opening, capture callback preference and end the current call.
6. Answer a relevant question or diversion briefly, using approved context only.
7. Ask the earliest unanswered checklist item, or perform the qualified-lead handoff only when every checklist item is complete and all applicable rules pass.

**Important:** the assignment says to disqualify immediately when a criterion fails, and to route existing-loan/EMI-reduction cases to a specialist. Do not keep asking standard qualification questions after either terminal branch is triggered.

## 3. Loan amount greater than ₹75 lakh

A request above the maximum is not an immediate disqualification.

1. Explain that this offer is available for up to ₹75 lakh.
2. Ask if the customer wants to proceed with ₹75 lakh.
3. If yes, store ₹75,00,000 as the selected amount and continue.
4. If no, end the call politely.
5. If the answer is unclear, ask for confirmation; do not assume acceptance.

## 4. Ownership and documents

- Joint ownership is eligible; do not equate joint ownership with ineligibility.
- Documents do not need to be physically held during the call. The requirement is that the original documents are available for verification.
- If availability is ambiguous (e.g. “I think the papers are somewhere”), clarify. Do not assume the criterion passes.

## 5. Facts not specified by the assignment

Do not invent:
- A minimum property market value.
- An exact interest rate.
- Additional eligibility thresholds or underwriting requirements.
- A guaranteed approval or disbursal outcome.

Where details such as an exact rate are not available in `additional_context_from_rag`, say that the senior loan expert will provide them.

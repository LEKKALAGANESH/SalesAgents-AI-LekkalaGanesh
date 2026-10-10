# Prompt Review and Scenario Validation

**Validation type:** Static prompt-logic review  
**Date:** 2026-10-10  
**Prompt reviewed:** [system-prompt.txt](../system-prompt.txt)  
**Important limitation:** These are expected-outcome checks against the written prompt. They are NOT live calls, speech-recognition tests, voice-platform tests, or recordings. Live testing must be performed after configuring the agent on Retell AI, Bolna, or another selected platform.

## Scenario review

| ID | Input / scenario | Expected result from prompt | Static review |
|---|---|---|---|
| V01 | Verified customer; residential, sole owner, originals available, ₹50 lakh, salaried, bank income, ₹1 crore value, 10 years | All seven items pass; expert follow-up | PASS — path specified |
| V02 | Agricultural property | Disqualify and end immediately | PASS — terminal rule explicit |
| V03 | Cash income | Disqualify and end immediately | PASS — terminal rule explicit |
| V04 | Original documents unavailable | Disqualify and end immediately | PASS — terminal rule explicit |
| V05 | Tenure 2 years | Disqualify | PASS — lower bound explicit |
| V06 | Tenure 16 years | Disqualify | PASS — upper bound explicit |
| V07 | Requests ₹90 lakh, accepts ₹75 lakh | Store ₹75 lakh and continue | PASS — explicit acceptance required |
| V08 | Requests ₹90 lakh, declines ₹75 lakh | End without continuing | PASS — terminal outcome specified |
| V09 | Joint ownership | Continue; no disqualification | PASS — explicitly allowed |
| V10 | Existing property loan | Transfer-specialist message and end | PASS — terminal branch specified |
| V11 | Wants EMI reduction | Transfer-specialist message and end | PASS — terminal branch specified |
| V12 | Gives property type, value, and joint ownership out of order | Capture all three; ask earliest missing item | PASS — algorithm and example included |
| V13 | Busy at opening | Ask callback time and end | PASS — terminal callback branch specified |
| V14 | Asks exact interest rate, context has no rate | Do not invent rate; refer to senior expert | PASS — fallback specified |
| V15 | Asks branch location, context has no answer | Do not invent location; return to checklist | PASS — grounded-answer rule specified |
| V16 | Gives several clear facts in one response | Store all; do not ask them again | PASS — extraction rule explicit |
| V17 | Corrects residential to agricultural | Latest clear answer wins; disqualify | PASS — correction rule explicit |
| V18 | Says documents are “probably somewhere” | Clarify; do not assume availability | PASS — ambiguity handling explicit |
| V19 | Interrupts to ask what information is needed | Answer only from approved facts, then resume at first missing item | PASS — interruption rule specified |
| V20 | All but one checklist item are known | Ask missing item; no handoff yet | PASS — handoff gate explicit |
| V21 | Exactly ₹75 lakh requested | Continue; amount is within cap | PASS — inclusive cap specified |
| V22 | Tenure exactly 3 or 15 years | Continue; both boundaries allowed | PASS — inclusive range specified |
| V23 | Low market-value estimate | Capture value; do not reject based on an invented minimum | PASS — no threshold rule explicit |
| V24 | Person says this is the wrong customer | Do not disclose offer details; end | PASS — verification safety specified |

## Findings / follow-up before live testing

1. **Prompt logic:** the main business branches and the 7-item handoff gate are represented explicitly.
2. **Platform configuration remains outstanding:** choose a platform, map template variables to its actual syntax, select voice settings, and configure call end / callback / specialist follow-up behavior.
3. **State persistence must be verified:** a prompt may describe state, but platform behavior can vary. If the platform supports structured variables or tools, use them for critical terminal flags and checklist fields.
4. **Live evidence remains outstanding:** execute actual calls, then replace this static review with observed pass/fail results and recording/transcript references.
5. **Production use requires a separate data-handling review:** confirm appropriate consent, access controls, retention, and redaction for recordings and customer data.

## Live run log

| Test | Live call status | Recording / transcript |
|---|---|---|
| Core happy path | Not run | Not available |
| Disqualification branches | Not run | Not available |
| Transfer branches | Not run | Not available |
| Diversions and interruptions | Not run | Not available |

Do not report static review as a successful voice-agent test.
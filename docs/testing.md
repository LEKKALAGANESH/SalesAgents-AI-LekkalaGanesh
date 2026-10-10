# Test Plan and Scenario Matrix

## 1. Testing approach

Run the prompt on the selected voice platform using natural-sounding customer utterances. For each test, record:
- Test ID and scenario.
- Input/customer utterance or call script.
- Expected state updates.
- Expected next response / terminal outcome.
- Actual result.
- Pass/fail and a reference to recording, transcript, or call log.
- Defect notes and regression-test status.

Do not mark tests as passing until the observed call behavior is checked.

## 2. Core scenario matrix

| ID | Scenario | Customer facts / utterance | Expected behavior |
|---|---|---|---|
| T01 | Happy path | Residential, sole ownership, originals available, ₹50 lakh, salaried, bank income, value ₹1 crore, 10 years | Complete all seven items; tell customer senior expert will follow up |
| T02 | Agricultural property | “It’s agricultural land.” | Immediate polite disqualification; no further checklist questions |
| T03 | Cash income | Self-employed; income received in cash | Immediate polite disqualification |
| T04 | Originals unavailable | “I only have photocopies; the originals aren’t available.” | Immediate polite disqualification |
| T05 | Tenure too short | “I’d like to repay it over two years.” | Disqualify because tenure is under 3 years |
| T06 | Tenure too long | “I need 20 years.” | Disqualify because tenure exceeds 15 years |
| T07 | Amount above cap; accepts | “I need ₹90 lakh.” Then “Yes, ₹75 lakh is fine.” | Explain maximum, get clear acceptance, record ₹75 lakh, continue |
| T08 | Amount above cap; declines | “I need ₹90 lakh.” Then “No, I need the full amount.” | End politely; do not continue qualification |
| T09 | Joint ownership | “It’s jointly owned by me and my brother.” | Record Joint; do not disqualify |
| T10 | Existing property loan | “I already have a loan against this property.” | Tell customer a specialist will contact them; end |
| T11 | EMI reduction | “I want to reduce the EMI on my current property loan.” | Transfer-specialist flow; end |
| T12 | Out-of-order answers | “It’s a residential house worth ₹1.2 crore, jointly owned with my wife.” | Record type, market value, ownership; ask earliest missing item (original-document availability) |
| T13 | Busy customer | “I’m in a meeting right now.” | Ask convenient callback time; capture it; end without pitching |
| T14 | Unknown interest rate | “What interest rate will I get?” with no rate in RAG context | Do not invent rate; explain senior expert will provide it; resume checklist |
| T15 | Unrelated question absent from context | “Where is your nearest branch?” but no branch data is supplied | Do not fabricate location; briefly explain limitation and return to checklist |
| T16 | Multiple facts together | “My home is residential and solely owned; originals are available. I need ₹40 lakh and prefer 10 years.” | Capture all clear facts; validate them; ask first missing item only |
| T17 | Correction to a failing answer | “It’s residential… actually, it’s agricultural.” | Use latest clear answer and disqualify |
| T18 | Ambiguous documents | “I think the papers are somewhere.” | Ask whether original documents are available for verification; do not assume |
| T19 | Interruption | Customer interrupts checklist to ask what documents are needed | Answer briefly without unsupported claims, then return to earliest missing item |
| T20 | Handoff gate | Customer appears eligible but one checklist item is missing | Do not hand off; ask the missing item |

## 3. Additional state and regression checks

- [ ] Missing values remain unknown rather than defaulting to eligible.
- [ ] A later explicit correction replaces the old value.
- [ ] Clear facts volunteered early are not re-asked.
- [ ] Every immediate disqualification stops the normal checklist.
- [ ] A transfer condition stops the normal checklist.
- [ ] No qualified handoff happens with missing values.
- [ ] ₹75 lakh exactly is accepted as within the cap.
- [ ] Tenure values 3 and 15 are accepted as inclusive boundaries.
- [ ] No minimum market-value threshold is introduced.
- [ ] Runtime variables are used rather than hardcoded persona details.
- [ ] English/Hindi setting and agent-gender setting are respected.
- [ ] Unknown product facts are not made up.
- [ ] The post-call outcome matches the transcript and observed customer answers.

## 4. Evidence table template

| Test ID | Run date | Result (Pass/Fail) | Recording / log link | Defect / follow-up |
|---|---|---|---|---|
| T01 | TBD | Not run | TBD | TBD |
| T02 | TBD | Not run | TBD | TBD |
| T03 | TBD | Not run | TBD | TBD |

Duplicate rows as needed for each executed run. Never label unexecuted tests as passed.

## 5. Release criteria

- Every required scenario has been executed.
- No critical failure remains in disqualification, transfer routing, amount-limit handling, state capture, or handoff gating.
- Failed scenarios have been fixed and rerun.
- Evidence links work for the intended reviewer audience.
- The final system prompt and tested configuration correspond to the same version.

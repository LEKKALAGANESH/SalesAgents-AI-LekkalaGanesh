# Tasks and Milestones

This is the proposed delivery backlog for the assignment. Mark tasks complete only after verifying the artifact or behavior.

## M0 — Understand and freeze requirements

- [ ] Read the assignment end-to-end.
- [ ] Confirm the seven checklist items and the policy for each.
- [ ] Confirm terminal branches: busy callback, transfer specialist, disqualification, qualified handoff.
- [ ] Confirm the required prompt variables.
- [ ] Record unresolved implementation choices in the PRD.

**Exit condition:** PRD and business-rule table agree with the source assignment.

## M1 — Design the conversation

- [ ] Define the call-state model.
- [ ] Define all qualification state fields and initial values.
- [ ] Specify the “extract → validate → update → next missing item” algorithm.
- [ ] Define interruption, diversion, correction, and ambiguity handling.
- [ ] Define the offer, disqualification, transfer, and handoff wording.
- [ ] Review gender and language-variable behavior.

**Exit condition:** conversation design covers each required branch and terminal state.

## M2 — Write the system prompt

- [ ] Use all assignment-provided variables.
- [ ] Define role, objective, identity, voice, and language.
- [ ] Embed eligibility rules without adding unsupported thresholds.
- [ ] Enforce immediate disqualification and transfer exits.
- [ ] Enforce the seven-item handoff gate.
- [ ] Include RAG-grounding rules and a safe fallback for unknown details.
- [ ] Verify natural language and out-of-order capture instructions.

**Exit condition:** one versioned, reviewable system prompt is ready to configure.

## M3 — Configure the voice platform

- [ ] Choose Retell AI, Bolna, or another suitable platform.
- [ ] Create the voice agent and select a professional voice.
- [ ] Configure the system prompt and variables.
- [ ] Configure any needed knowledge/context injection.
- [ ] Determine how the platform produces a public recording and call-log link.
- [ ] Make a controlled test call.

**Exit condition:** a test call can be run and its transcript/recording can be accessed.

## M4 — Validate behavior

- [ ] Run all core scenarios in [testing.md](testing.md).
- [ ] Confirm every terminal branch stops the normal flow.
- [ ] Confirm already-provided answers are not repeated.
- [ ] Confirm latest corrections overwrite earlier answers.
- [ ] Confirm ambiguous data triggers clarification.
- [ ] Record actual result and expected result for each test.
- [ ] Fix failures and rerun affected tests.

**Exit condition:** each required scenario has evidence and no known critical rule violation.

## M5 — Prepare submission

- [ ] Save the final system prompt as a Markdown or text file.
- [ ] Capture test recordings for different scenarios.
- [ ] Capture transcripts and call logs.
- [ ] Create a public share link for the required call evidence, checking access permissions.
- [ ] Review the repository docs for consistency.
- [ ] Complete [submission-checklist.md](submission-checklist.md).

**Exit condition:** required deliverables are ready and links have been verified.

## Suggested priority

| Priority | Work |
|---|---|
| P0 | Business rules, state model, system prompt, terminal-branch tests |
| P1 | Interruption/diversion handling, broad scenario matrix, recordings |
| P2 | Documentation polish, traceability, optional implementation notes |

## Definition of done

The assignment is not done merely because the prompt is written. The prompt must be configured on a voice platform, exercised through multiple calls, and supported by the required system-prompt and call-evidence deliverables.

# SalesAgents AI — Documentation Hub

This directory is the source of truth for the SalesAgents AI voice-agent assignment: a conversational AI agent that conducts preliminary Home Credit Loan Against Property (LAP) qualification calls.

## Start here

| Document | Purpose |
|---|---|
| [Product Requirements Document](prd.md) | Product goal, users, scope, requirements, acceptance criteria |
| [Business Rules](business-rules.md) | Eligibility policy and mandatory routing rules |
| [Tasks and Milestones](tasks.md) | Implementation backlog and completion checklist |
| [Development Process](process.md) | End-to-end delivery workflow and quality gates |
| [Architecture](architecture.md) | Proposed system boundaries, state, data flow, integrations |
| [Conversation Design](design.md) | Call states, dialog behavior, voice and diversion rules |
| [Testing Plan](testing.md) | Happy paths, failures, edge cases, adversarial scenarios |
| [System Prompt Guide](system-prompt.md) | Prompt structure, variables, guardrails, state-management algorithm |
| [Prompt Review Results](prompt-review-results.md) | Static scenario review and outstanding live-test requirements |
| [Submission Checklist](submission-checklist.md) | Required artifacts and final verification |

## Deployable prompt

The current draft is at [`../system-prompt.txt`](../system-prompt.txt). It is written as a platform-neutral prompt template; replace or map placeholders to the syntax supported by the selected voice platform before deployment.

## Project status

- **Status:** Documentation and assignment planning.
- **Implementation status:** Not assessed. The repository was empty when this documentation set was initialized.
- **Target use case:** Preliminary qualification for a fresh Loan Against Property offer.
- **Voice platform:** To be selected (the assignment permits Retell AI, Bolna, or a similar platform).

## Normative source

The rules in these documents are derived from the supplied **Voice Agent Design** assignment. When a requirement is not specified by the assignment, it is explicitly marked as a proposal or open decision rather than treated as a confirmed business rule.

## Suggested delivery order

1. Confirm requirements and business rules.
2. Design the conversation state machine and qualification state.
3. Write and review the system prompt.
4. Configure the selected voice platform.
5. Execute the test matrix and fix failures.
6. Capture call recordings, transcripts, and logs.
7. Complete the [submission checklist](submission-checklist.md).

## Documentation conventions

- **MUST / MUST NOT** denote mandatory assignment behavior.
- **SHOULD** denotes a strong recommended practice.
- **Proposed** denotes an implementation design that still needs confirmation.
- Keep this hub updated whenever documents are added or renamed.

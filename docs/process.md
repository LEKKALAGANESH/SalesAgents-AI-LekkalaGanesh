# Development Process

## Overview

Use a requirements-first workflow so the prompt is derived from explicit rules rather than improvised from examples.

```text
Assignment
   ↓
Requirements and business rules
   ↓
Conversation state machine
   ↓
System prompt
   ↓
Voice-platform configuration
   ↓
Happy-path tests
   ↓
Failure and edge-case tests
   ↓
Prompt fixes and regression tests
   ↓
Recordings, transcripts, and submission review
```

## Phase 1 — Requirement extraction

1. Read the assignment and identify every mandatory requirement.
2. Separate conversation behavior from eligibility policy.
3. Record all variables the platform will inject.
4. Write down unspecified areas; do not silently fill them with assumed policy.

**Gate:** each requirement is documented in the PRD and/or business rules.

## Phase 2 — Model states and decisions

1. Model call-level states, including verification, availability, offer presentation, qualification, and terminal outcomes.
2. Initialize eligibility fields as unknown.
3. Define how facts are extracted from free-form customer speech.
4. Make transfer and disqualification exits explicit.
5. Require all seven checklist items before the qualified handoff.

**Gate:** each business rule maps to a decision, state transition, or test.

## Phase 3 — Author the prompt

1. Use clear sections rather than one unstructured paragraph.
2. Define identity, language, gender, objective, and variables.
3. Add concise dialog examples only where they clarify behavior.
4. Add the fixed processing algorithm and terminal-branch instructions.
5. Specify how to use approved RAG context and how to respond when information is missing.

**Gate:** prompt review finds no contradictions or unsupported eligibility rules.

## Phase 4 — Configure the platform

1. Select a suitable voice-agent platform (Retell AI, Bolna, or similar).
2. Configure voice and system prompt.
3. Map runtime variables to the platform's supported inputs.
4. Verify whether state, knowledge retrieval, logging, and handoff are prompt-only or require platform configuration.
5. Make a controlled smoke-test call.

**Gate:** the configured agent can run a test call and produce usable call evidence.

## Phase 5 — Test and improve

1. Run a clean eligible case first.
2. Run one test for each disqualifying criterion.
3. Test amount-over-limit negotiation and transfer routing.
4. Test busy customers, out-of-order facts, interruptions, diversions, corrections, and ambiguous values.
5. Compare observed results with expected results.
6. Adjust the prompt/configuration, then rerun failed cases plus regression cases.

**Gate:** tests show expected behavior across the required scenarios.

## Phase 6 — Prepare and review submission

1. Save the final prompt and supporting explanation.
2. Collect call recordings, transcripts, and logs.
3. Verify each share link using a session that does not have owner-only access, where feasible.
4. Check that no sensitive customer data is exposed in public evidence.
5. Complete the checklist and review documentation links.

**Gate:** the required submission artifacts are present and accessible.

## Change management

When a rule changes:
1. Update [business-rules.md](business-rules.md).
2. Update affected PRD acceptance criteria, conversation design, prompt guidance, and test cases.
3. Rerun every test linked to that rule.
4. Record the change in the commit message or project notes.

Do not change an eligibility decision in only one document while leaving the others inconsistent.

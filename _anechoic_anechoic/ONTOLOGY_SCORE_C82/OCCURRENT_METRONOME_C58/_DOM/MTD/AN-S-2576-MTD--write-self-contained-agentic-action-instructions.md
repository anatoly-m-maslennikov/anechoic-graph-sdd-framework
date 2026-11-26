---
atom_family: SPEC
atom_id: AN-S-2576
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: active
  version: 28
  updated_at: '2026-11-25T21:00:37.821651+00:00'
---
## Summary
Write self-contained agentic Action instructions

## Claim

### Prose Claim

derived instructions that present an Agentic Action for execution.


**to** present an Agentic Action for execution, organize its derived instruction around the declared responsibility rather than assumed session memory.

- state the requested outcome, relevant context, exact targets, inputs, available evidence, **and** governing references.
- distinguish already performed effects from proposed changes, **and** existing permissions from decisions still needed.
- state the expected result **and** how **to** report uncertainty, failures, partial effects, **or** a request for Operator input. do **not** treat a suggested correction as permission **to** apply it.
- keep the instruction limited **to** the bound Action. leave next-Step selection **and** cross-Workflow handoff coordination **to** the executor using the governing Workflow.
- use understandable wording **and** structured points under AN-S-2301 and AN-S-2504; reference governing definitions rather than copying another authoritative procedure into the prompt.
- keep internal Tool calls as execution detail under AN-S-1618. **when** an operation needs independently governed routing, checks, **or** approval boundaries, express it as an explicit Step during Workflow authoring rather than inventing Workflow nodes from runtime calls.

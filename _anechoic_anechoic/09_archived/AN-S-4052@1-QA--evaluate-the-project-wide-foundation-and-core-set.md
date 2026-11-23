---
atom_family: SPEC
atom_id: AN-S-4052
container:
  component: C00
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 22:26:56 +0400
---
## Summary

Evaluate the Project-wide foundation and Core set

## Claim

The Project-wide foundation and Core set Evaluation **must** return `fail` **if** a known Project-wide invariant has no canonical owner, a Project-wide foundational commitment is **only** a narrow application rather than a broad commitment, a required supporting Core Claim is absent, Claims conflict **or** independently duplicate authority **in** the same context, **or** an Atom has an incompatible Local Tier **or** Content Role; **otherwise**, it **may** return `pass` for the reviewed frontier **without** claiming that undiscovered gaps are impossible. Evaluate the Content Roles of Project-wide foundational commitments under CA-E-661; the former Actor-policy interpretation of Plan does **not** create an exception **to** current Content Role authority. Faithful Core specialization **must not** count as duplicate authority; fixed child counts, a universal RMED checklist per Project-wide foundational commitment, expansion from Intent, **and** formula/text equivalence **must not** be acceptance conditions. Report missing support **and** conflicting owners **to** the Operator **without** silently selecting a winner.

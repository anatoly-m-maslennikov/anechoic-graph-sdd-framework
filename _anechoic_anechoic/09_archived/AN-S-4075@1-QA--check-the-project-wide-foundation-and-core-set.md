---
atom_family: SPEC
atom_id: AN-S-4075
container:
  component: C00
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-30 03:11:57 +0400
---
## Summary

Check the Project-wide foundation and Core set

## Claim

The Project-wide foundation and Core set Evaluation **must** return `fail` **if** **any** of the following applies:

- A known Project-wide invariant has no canonical owner;
- A Project-wide foundational commitment is **only** a narrow application rather than a broad commitment;
- A required supporting Core Claim is absent;
- Claims conflict **or** independently duplicate authority **in** the same context; **or**
- An Atom has an incompatible Local Tier **or** Content Role.

**otherwise**, the Evaluation **may** return `pass` for the reviewed frontier **without** claiming that undiscovered gaps are impossible.

Evaluate the Content Roles of Project-wide foundational commitments by checking whether each Atom's complete primary contribution matches its applicable Content Role definition. The former Actor-policy interpretation of Plan does **not** create an exception **to** current Content Role authority.

Faithful Core specialization **must not** count as duplicate authority. **none** of the following **may** be acceptance conditions:

- fixed child counts;
- A universal RMED checklist per Project-wide foundational commitment;
- expansion from Intent; **or**
- formula/text equivalence.

Report missing support **and** conflicting owners **to** the Operator **without** silently selecting a winner.

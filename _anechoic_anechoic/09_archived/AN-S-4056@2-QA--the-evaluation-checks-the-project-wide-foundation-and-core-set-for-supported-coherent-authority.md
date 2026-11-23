---
atom_family: SPEC
atom_id: AN-S-4056
container:
  component: C00
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-10-30 01:32:01 +0400
---
## Summary

The Evaluation checks the Project-wide foundation and Core set for supported, coherent authority

## Claim

the Project-wide foundation and Core set Evaluation **must** return `fail` **if** **any** of the following applies:

- a known Project-wide invariant has no canonical owner;
- a Project-wide foundational commitment is **only** a narrow application rather than a broad commitment;
- a required supporting Core Claim is absent;
- Claims conflict **or** independently duplicate authority **in** the same context; **or**
- an Atom has an incompatible Local Tier **or** Content Role.

**otherwise**, the Evaluation **may** return `pass` for the reviewed frontier **without** claiming that undiscovered gaps are impossible.

the Evaluation **must** evaluate each Project-wide foundational commitment's Content Role against its complete primary contribution **and** applicable Content Role definition. the Scope Contract Tier Label alone does **not** change its Content Role **or** Type. the former Actor-policy interpretation of Plan does **not** create an exception **to** current Content Role authority.

faithful Core specialization **must not** count as duplicate authority. **none** of the following **may** be an acceptance condition:

- fixed child counts;
- a universal RMED checklist per Project-wide foundational commitment;
- expansion from Intent; **or**
- formula/text equivalence.

the Evaluation **must** report missing support **and** conflicting owners **to** the Operator **without** silently selecting a winner.

---
atom_family: SPEC
atom_id: AN-S-1886
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-11 18:11:33 +0400
---
## Summary

Check the selected Scope against active Project-wide invariants

## Claim

### Prose Claim


For **every** selected Scope, the complete set of active Atoms **must** align with **every** active Project-wide foundational invariant.

## Check

Load the complete active Project-wide foundational invariant set first. Resolve the Scope **and** collect the complete active Atom set, including Methodology source Atoms within the selected Scope. Evaluate **every** Atom against **every** Project-wide foundational invariant **before** applying lower-tier authority.

## Acceptance

Pass **only** **when** **both** of the following hold:

- no Atom conflicts with a Project-wide foundational invariant; **and**
- no lower-tier interpretation weakens **or** overrides a Project-wide foundational invariant.

## Failure

Report **every** conflicting Atom **and** Project-wide foundational invariant pair. Route **every** conflict between active Project-wide foundational invariants **to** the Operator under `CA-R-2425-CORE_META_MODEL-RULE--reserve-project-wide-invariant-conflict-resolution-to-the-operator`.

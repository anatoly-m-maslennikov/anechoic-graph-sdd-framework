---
atom_family: SPEC
atom_id: AN-S-1794
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-27 19:59:59 +0400
---
## Summary

Allow pre-runtime pass only with sufficient evidence

# Summary

Allow pre-runtime pass only with sufficient evidence

## Scope

Evaluations using a Realization Graph before runtime, for their declared input boundary.

## Claim

an Evaluation using a Realization Graph **may** return `pass` **before** runtime **only** **when** sufficient evidence establishes the checked Claim for the declared input boundary.

- **if** the Claim requires complete coverage of particular Relation mechanisms, the evidence **must** establish that coverage; a completeness declaration alone is insufficient.
- the evidence **must** establish the actual acceptance condition. complete provenance **or** graph coverage does **not** itself establish that condition.
- a possible inferred Relation is **not** an observed occurrence. **when** required runtime evidence is unavailable **or** a material condition remains unresolved, the Evaluation **must not** return a pre-runtime `pass`.

this Claim constrains permission **to** report a result; the applicable E Atoms supply the checks. it does **not** require complete graph coverage for a Claim that needs **only** bounded evidence.

## Details

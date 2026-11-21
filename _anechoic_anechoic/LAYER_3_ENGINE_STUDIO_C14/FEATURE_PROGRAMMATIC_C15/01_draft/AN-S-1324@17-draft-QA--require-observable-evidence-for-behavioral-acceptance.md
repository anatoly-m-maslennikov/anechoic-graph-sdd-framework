---
atom_family: SPEC
atom_id: AN-S-1324
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: draft
  version: 17
  updated_at: '2026-11-14T08:28:33.018161+00:00'
---
## Summary
Require observable evidence for behavioral acceptance

## Claim
### Prose Claim
Behavioral software Evaluation can support acceptance only if every declared failure predicate has at least one reproducible check.
A check must not make acceptance depend only on replaceable private Implementation structure when a semantic or public behavior boundary can expose the predicate.

## Details
### Scope
This foundational evidence boundary applies to PROGRAMMATIC components and the applicable Spec.
Apply CA-E-389 for portfolio acceptance and cost. This Atom sets no test-scope ratio.

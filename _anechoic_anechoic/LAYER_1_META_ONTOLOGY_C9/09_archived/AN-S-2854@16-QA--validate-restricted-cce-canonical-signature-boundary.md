---
atom_family: SPEC
atom_id: AN-S-2854
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Validate Restricted CCE Canonical Signature Boundary

# Summary

Validate Restricted CCE Canonical Signature Boundary

## Scope

Canonical Signature derivations evaluated against the restricted CCE boundary.

## Claim

the Evaluation **must** reject a Canonical Signature derivation **if** any of the following is true:

- it rewrites one source Claim.
- it treats one Canonical Signature as authority.
- it accepts mixed **and** **or** groups.
- it rewrites negation, implication, **where**, **without**, temporal condition, quantifier, extension-defined CCE Operator, **or** unparseable prose.
- it fails **to** flatten nested same-operator groups.
- it retains duplicate atomic predicates.
- it yields different Canonical Signatures from Boolean groups that differ **only** by operand order.

## Details

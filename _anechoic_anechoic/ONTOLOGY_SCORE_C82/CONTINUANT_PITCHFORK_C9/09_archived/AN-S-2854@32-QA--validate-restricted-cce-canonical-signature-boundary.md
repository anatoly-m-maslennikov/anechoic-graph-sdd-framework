---
atom_family: SPEC
atom_id: AN-S-2854
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 32
  updated_at: '2026-11-13T19:05:24.789743+00:00'
---
## Summary

Validate Restricted CCE Canonical Signature Boundary

## Claim

### Prose Claim


Canonical Signature derivations evaluated against the restricted historical CCE boundary. This Evaluation does not establish a signature for ASD-STE100-aligned prose.


the Evaluation **must** reject a Canonical Signature derivation **if** any of the following is true:

- it rewrites one source Claim.
- it treats one Canonical Signature as authority.
- it accepts mixed **and** **or** groups.
- it rewrites negation, implication, **where**, **without**, temporal condition, quantifier, extension-defined CCE Operator, **or** unparseable prose.
- it fails **to** flatten nested same-operator groups.
- it retains duplicate atomic predicates.
- it yields different Canonical Signatures from Boolean groups that differ **only** by operand order.

---
atom_family: SPEC
atom_id: AN-S-2512
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: active
  version: 31
  updated_at: '2026-11-13T19:03:29.276423+00:00'
---
## Summary

Validate Canonical Scope Signature Boundary

## Claim

### Prose Claim


Canonical Scope Signature derivations from historical CCE material. This Evaluation does not establish a prose profile for new Atoms.


the Evaluation **must** reject a Canonical Scope Signature derivation **if** **any** of the following holds:

- it rewrites one source Carrier.
- it treats one Signature as authority **or** Claim equivalence.
- it accepts mixed **and** **or** groups, **without**, **where**, **all**, **any** other CCE Operator, function, Entity-kind selector, descendant **or** dynamic selector, unresolved identity, changing source frontier, **or** unparseable prose.
- it fails **to** flatten nested same-operator groups, retains duplicate exact Atom IDs, loses the distinction between **and** **and** **or**, **or** yields different Signatures from same-operator groups that differ **only** by operand order.

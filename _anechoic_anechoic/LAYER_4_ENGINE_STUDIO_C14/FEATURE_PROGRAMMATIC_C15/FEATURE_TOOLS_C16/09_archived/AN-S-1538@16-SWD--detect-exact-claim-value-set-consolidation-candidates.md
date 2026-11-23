---
atom_family: SPEC
atom_id: AN-S-1538
container:
  component: C16
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 18:38:52 +0400
---
## Summary

Detect Exact Claim Value-Set Consolidation Candidates

# Detect Exact Claim Value-Set Consolidation Candidates

**to** detect Claim Value Set consolidation candidates, the `DETECT_CLAIM_VALUE_SET_CANDIDATES` Tool **must** inspect one Scope Unit's local active Atom frontier **without** its child Scope Unit frontiers, derive **every** Atom's Governed Subject Set from its GOVERNS Subjects, derive its Claim Scope from the Property **in** one exact `<Property>: <Value>[ **if** <Qualifier>].` Claim, accept a value **only** **if** one supplied Entity Graph Projection proves its IS_ALLOWED_VALUE_OF relation for that Property, group **only** identical Current Scope Owner, Governed Subject Set, Claim Scope, Property, **and** qualifier coordinates, report **every** contributing Atom ID **and** one proposed `Property: (A, B, C)` Claim, **and** report no candidate for unparseable, unproven, **or** semantically similar prose.

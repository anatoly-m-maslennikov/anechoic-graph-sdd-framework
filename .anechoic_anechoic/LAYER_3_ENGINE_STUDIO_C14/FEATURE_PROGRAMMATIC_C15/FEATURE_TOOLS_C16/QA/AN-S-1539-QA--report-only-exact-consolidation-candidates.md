---
identity:
  atom_id: AN-S-1539
context:
  container:
    component: C16
  tier: 2
  lens: QA
state:
  status: active
  version: 24
  updated_at: 2026-10-27 19:59:34 +0400
---
## Summary

Report Only Exact Consolidation Candidates

# Report Only Exact Consolidation Candidates

## Test case

provide one active Source frontier containing: two mechanically parseable
single-value Claims with the same Current Scope Owner, Governed Subject Set,
Claim Scope, Property, **and** qualifiers but different unique values; one semantically similar prose Claim;
one Claim with a different qualifier; **and** one unparseable Claim.
place one Claim that differs from a qualifying Claim **only** by its location **in** one child Scope Unit frontier.

pass **only** **when** the Tool reports **`=1`** consolidation candidate containing
the two qualifying Atom IDs **and** one proposed `Property: (A, B)` Claim, reports no
candidate from the other Claims, **and** leaves **every** Source carrier unchanged.
the child Scope Unit Claim **must not** enter the candidate.
fail **when** candidate membership depends on semantic inference, **any** required
identity is missing, an ineligible Claim is included, an eligible Claim is
omitted, **or** **any** Source carrier is mutated.

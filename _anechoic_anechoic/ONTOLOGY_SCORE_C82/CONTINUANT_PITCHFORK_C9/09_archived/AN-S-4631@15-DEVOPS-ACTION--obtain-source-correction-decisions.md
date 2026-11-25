---
atom_family: SPEC
atom_id: AN-S-4631
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Obtain source correction decisions

# Summary

Obtain source correction decisions

## Operation

Obtain Source Correction Decision **means** the reusable Action that obtains the Operator's explicit decision about an exact conflict-resolution proposal.

1. present the proposal, the conflict it addresses, **and** the selected source frontier **to** the Operator.
2. request an explicit decision. distinguish approval, rejection, requested revision, **and** absence of a decision; confidence, inferred intent, **or** an LLM judgment is **not** approval.
3. retain the actual decision with its proposal, conflict, exact source-frontier binding, **and** provenance in admitted execution evidence. attempt the Journal append as a business-provenance record; an append failure yields a `recording_error` diagnostic and does not change the decision **or** block authorization. record a missing decision as missing, **not** as an approval **or** rejection.
4. return the actual decision and its independently verified execution evidence for the applicable authorization checks. a changed proposal **or** source frontier requires the decision's applicability **to** be checked again **before** reliance.

this Action **must not** apply the correction, record approval the Operator did **not** give, **or** create a duplicate approval Atom **in** Project Configuration. the Journal append is a business-provenance obligation; it does **not** independently redefine the governing source Claims **or** serve as proof, permission, completion, **or** recovery gate.

## Details

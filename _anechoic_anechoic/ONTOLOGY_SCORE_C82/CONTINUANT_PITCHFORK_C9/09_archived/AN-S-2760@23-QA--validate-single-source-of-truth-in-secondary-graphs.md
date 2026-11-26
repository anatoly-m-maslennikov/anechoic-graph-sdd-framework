---
atom_family: SPEC
atom_id: AN-S-2760
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Validate Single Source of Truth in secondary graphs

# Summary
Validate Single Source of Truth in secondary graphs

## Scope
source authority **in** secondary graph representations.

## Claim
the Evaluation **must** distinguish authoritative source facts from their secondary graph representations **and** reject a Projection that acquires independent authority for a represented fact.

### Test cases

| Case | Expected result |
|---|---|
| **`=1`** source Claim represented **in** multiple graphs | pass **if** **all** representations retain the same source identity **and** applicable Revision |
| two independently maintained authoritative declarations for the same fact **in** the same context, even **when** their values agree | fail |
| different Claims **or** different source facts used by a derived result | no Single Source of Truth failure merely because there are multiple source Atoms |
| a permitted derived Relation with identified derivation authority **and** source inputs, but no separately authored declaration for its computed result | pass this source-authority check |
| a derived edge with no admitted derivation authority **or** missing required source evidence | fail **or** report unresolved evidence; do **not** invent a source declaration |
| a source Atom reached through another Projection | pass **if** ultimate source traceability is retained |
| a Journal event **or** structural fact represented **in** a graph | pass **if** its existing source authority remains intact; do **not** fabricate an Atom Claim as historical **or** observed evidence |
| a projected fact corrected independently while its source **and** governing derivation remain unchanged | fail |

passing this source-authority Evaluation does **not** establish graph-specific Relation validity, completeness, **or** the truth of a recorded outcome; those remain subject **to** their applicable Evaluations.

## Details

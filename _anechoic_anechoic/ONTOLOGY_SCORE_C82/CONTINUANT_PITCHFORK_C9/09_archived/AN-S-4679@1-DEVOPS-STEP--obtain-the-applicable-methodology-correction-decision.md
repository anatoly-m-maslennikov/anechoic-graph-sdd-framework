---
atom_family: SPEC
atom_id: AN-S-4679
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 17:42:12 +0000
---
## Summary

Obtain the Applicable Methodology correction decision

# Summary

Obtain the Applicable Methodology correction decision

## Operation

this Step is the decide node **of** CA-O-011, Applicable Methodology Compilation, invoking **`=1`** Action, CA-O-007, Obtain Source Correction Decision.

### Inputs and parameters

bind the exact proposal from CA-O-154, conflict and source-frontier digest from CA-O-153, and the Workflow Run's required Operator approval context and canonical Journal reference.

enforce CA-R-1317 through CA-O-007: obtain **`=1`** unambiguous actual Operator approval **and** record it **in** the Journal, bound **to** the exact proposal, conflict, **and** source-frontier digest. stale, partial, missing, ambiguous, **or** mismatched approval does **not** qualify. do **not** create an approval Atom **in** Project Configuration; approval **must not** itself bypass Core expansion boundaries.

## Details

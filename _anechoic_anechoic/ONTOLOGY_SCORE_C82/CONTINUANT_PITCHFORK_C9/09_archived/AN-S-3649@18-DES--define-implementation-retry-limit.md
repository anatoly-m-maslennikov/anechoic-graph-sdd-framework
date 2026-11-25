---
atom_family: SPEC
atom_id: AN-S-3649
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-29 07:17:17 +0400
---
## Summary

Define Implementation Retry Limit

# Summary

Define Implementation Retry Limit

## Scope

Implementation Retry Limit values in an Implementation Workflow Run.

## Claim

Implementation Retry Limit **means** the maximum number of additional fix-and-evaluate rounds permitted **after** the initial failed Evaluation **in** one Implementation Workflow Run.

- its value **must** be an integer **`>=0`**.
- a value **`=0`** permits no retry **after** the initial failure.
- the limit does **not** grant permission **to** repair, change authority, **or** bypass an applicable confidence threshold.

## Details

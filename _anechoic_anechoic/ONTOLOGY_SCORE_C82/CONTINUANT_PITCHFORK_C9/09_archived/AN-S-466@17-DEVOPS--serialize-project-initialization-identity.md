---
atom_family: SPEC
atom_id: AN-S-466
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 17
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Serialize Project initialization identity

# Summary

Serialize Project initialization identity

## Scope

the Operator-selected Project Name in the Project Settings TOML Carrier.

## Claim

the Project Settings TOML Carrier **must** encode the Operator-selected Project Name as its exact nonempty lowercase TOML string value **in** `project.name`, **before** the first Project Atom **or** Implementation is created.

## Details

validation **must** preserve the selected value exactly; it **must not** trim **or** convert its case. the complete supported field signature is governed by CA-D-366.

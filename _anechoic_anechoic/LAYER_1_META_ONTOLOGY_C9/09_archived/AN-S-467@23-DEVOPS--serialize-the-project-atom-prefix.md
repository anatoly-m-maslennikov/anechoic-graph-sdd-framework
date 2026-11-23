---
atom_family: SPEC
atom_id: AN-S-467
container:
  component: C9
tier: 7
context:
  lens: DevOps
state:
  status: archived
  version: 23
  updated_at: 2026-10-27 19:59:24 +0400
---
## Summary

Serialize the Project Atom prefix

# Summary

Serialize the Project Atom prefix

## Scope

the Operator-selected Atom prefix in the Project Settings TOML Carrier.

## Claim

the Project Settings TOML Carrier **must** encode the Operator-selected Atom prefix as its exact nonempty uppercase TOML string value under CA-D-378 **in** `artifacts.identity.project_prefix` **before** the first Project Atom is created.

## Details

validation **must** preserve the selected prefix exactly; it **must not** trim **or** automatically uppercase it. the complete supported field signature is governed by CA-D-366.

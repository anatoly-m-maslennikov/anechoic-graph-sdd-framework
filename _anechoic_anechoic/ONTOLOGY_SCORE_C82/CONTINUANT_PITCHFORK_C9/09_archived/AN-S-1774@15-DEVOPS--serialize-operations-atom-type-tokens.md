---
atom_family: SPEC
atom_id: AN-S-1774
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Serialize Operations Atom Type tokens

# Summary

Serialize Operations Atom Type tokens

## Scope

Operations Atom File Carriers and their Type filename tokens.

## Claim

an Operations Atom File Carrier **must** serialize its Type using this filename-token mapping:

| Operations Atom Type | Filename token |
|---|---|
| Action | `ACTION` |
| Workflow | `WORKFLOW` |
| Step | `STEP` |
| Actor | `ACTOR` |

## Details

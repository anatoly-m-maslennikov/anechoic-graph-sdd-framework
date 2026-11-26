---
atom_family: SPEC
atom_id: AN-S-3403
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-20 20:14:40 +0400
---
## Summary

Define Artifact Revision

# Summary

Define Artifact Revision

## Scope

Preserved historical states of Artifacts.

## Claim

a Revision **means** a preserved historical state of an Artifact. it belongs to History; it is **not** a dependent property of the current Artifact. the preserved state **must not** be edited as though it were the current state.

## Details

A current Atom remains an Atom with its own Version Number and Updated At. Its accepted updates follow CA-R-1432 and CA-R-1788. An archived Atom itself represents the earlier Atom state; no additional Revision wrapper is required. This definition does not require a separate snapshot operation, Journal record, historical baseline or permission check. Journal records describe events, not Journal snapshots.


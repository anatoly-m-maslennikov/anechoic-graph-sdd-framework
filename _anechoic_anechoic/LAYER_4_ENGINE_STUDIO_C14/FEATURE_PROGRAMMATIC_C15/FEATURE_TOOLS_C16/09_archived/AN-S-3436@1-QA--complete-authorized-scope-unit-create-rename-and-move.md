---
atom_family: SPEC
atom_id: AN-S-3436
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Complete authorized Scope Unit Create, Rename, and Move

# Summary

Complete authorized Scope Unit Create, Rename, and Move

## Scope

Golden functional cases against a disposable project with declared TOML authority and independently observed implementation paths.

## Claim

The Evaluation **must** prove an authorized Create, Rename, and Move produce the expected tree and repaired reference sets through the real workflow boundary.

## Details

- Create an Ordered unit with a valid unique sibling `local_order`; Rename it and Move it under a valid parent.
- Assert authoritative TOML changes, distinct authority/delivery paths, cycle-free declarations, repaired incoming references/parent-owned attachments, reported Carrier observations, and exact result revisions.
- Assert no unrelated Carrier is deleted, all required Workflow/Action result references are returned where execution occurred, and shared Journal evidence is inspected through its existing contract.

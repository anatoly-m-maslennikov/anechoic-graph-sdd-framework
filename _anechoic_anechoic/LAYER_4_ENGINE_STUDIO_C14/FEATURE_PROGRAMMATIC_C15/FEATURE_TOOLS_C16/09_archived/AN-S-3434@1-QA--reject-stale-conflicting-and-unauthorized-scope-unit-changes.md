---
atom_family: SPEC
atom_id: AN-S-3434
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

Reject stale, conflicting, and unauthorized Scope Unit changes

# Summary

Reject stale, conflicting, and unauthorized Scope Unit changes

## Scope

Negative functional cases for currentness, declaration constraints, and approval boundaries.

## Claim

The Evaluation **must** prove the Tool stops before mutation for stale state, duplicate identity/order, a parent cycle, an Unordered `local_order`, or insufficient exact authorization.

## Details

- Mutate the selected TOML/references after preparation to obtain `stale`; submit duplicate identity/order and a parent cycle to obtain `conflict`; submit a folder-only observation or expired/insufficient approval to obtain `permission_denied` or `blocked`.
- Assert unchanged authoritative declarations and Carrier content for every case, exact failure reason and affected set, and no fabricated Run where dispatch never began.

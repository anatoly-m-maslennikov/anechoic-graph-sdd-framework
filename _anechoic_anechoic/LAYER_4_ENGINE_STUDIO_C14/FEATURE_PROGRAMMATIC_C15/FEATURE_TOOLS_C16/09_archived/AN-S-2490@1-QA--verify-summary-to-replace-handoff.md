---
atom_family: SPEC
atom_id: AN-S-2490
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

Verify Summary-to-Replace handoff

# Summary

Verify Summary-to-Replace handoff

## Scope

One sealed Update request that changes its Summary.

## Claim

Verify the dispatcher returns `replace_handoff` with the exact predecessor and proposed successor inputs, performs no same-ID update, and preserves the predecessor unchanged in preview. Apply an admitted Replace through the native Tool and verify explicit predecessor/successor lineage and observed history. Verify an unchanged Summary selects Update only when its native class permits it.

## Details

### Acceptance criteria

No Summary-changing request silently mutates the existing Atom identity. Replace results have both carrier identities; preview has neither mutation nor invented history.

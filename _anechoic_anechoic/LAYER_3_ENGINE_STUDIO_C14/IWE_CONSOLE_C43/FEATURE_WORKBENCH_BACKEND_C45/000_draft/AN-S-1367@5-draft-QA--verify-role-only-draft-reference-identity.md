---
atom_family: SPEC
atom_id: AN-S-1367
structure:
  container:
    component: C45
  tier: 6
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T23:58:37.308818+00:00'
---
## Summary

Verify role-only Draft reference identity.

## Claim

### Prose Claim

Verify that role-only Draft carriers with the same Atom ID remain distinct.

## Details

### Shared Atom ID

- Keep every carrier.
- Keep the Atom ID unchanged.
- Give each carrier a unique technical reference using the role-only ID
  and Project-relative carrier path.

### Coverage

- Verify six `CA-O-draft` lifecycle carriers under distinct paths.
- Verify that numbered Draft and Current canonical references stay unchanged.

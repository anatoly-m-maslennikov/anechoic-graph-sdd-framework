---
atom_family: SPEC
atom_id: AN-S-1367
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify role-only Draft reference identity.

## Claim

### Prose Claim

When multiple role-only Draft carriers use the same Atom ID, source capture
preserves every carrier and keeps that Atom ID unchanged. Each carrier receives
a unique technical `ref` formed from the role-only ID and its project-relative
carrier path, and the derived Projection retains all of the carriers without a
duplicate technical reference.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Six lifecycle Draft carriers with `atom_id: CA-O-draft` under distinct paths | All six carriers remain in capture and materialization; each has a distinct `CA-O-draft:<relative path>` reference. |
| Numbered Draft and Current carriers | Their existing canonical references remain unchanged. |

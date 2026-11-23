---
atom_family: SPEC
atom_id: AN-S-4257
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify default-off code hot reload

## Claim

### Prose Claim

For each code hot-reload mechanism, verify that ordinary startup leaves it disabled with no reload-only process/watcher, explicit opt-in enables it, and turning it off restores normal restart behavior. Verify that retained runtime capabilities and source-data synchronization still work in default mode. Test public launch/configuration behavior rather than internal implementation structure.

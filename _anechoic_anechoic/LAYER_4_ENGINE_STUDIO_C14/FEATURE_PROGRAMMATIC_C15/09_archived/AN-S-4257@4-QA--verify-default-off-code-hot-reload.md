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
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify default-off code hot reload

## Claim

### Prose Claim

For each hot-reload mechanism, ordinary startup is disabled without reload-only watcher/process; explicit opt-in enables it and disabling restores normal restart behavior. Verify retained runtime capabilities/source-data synchronization via public launch/configuration behavior.

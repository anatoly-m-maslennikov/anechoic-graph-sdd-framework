---
atom_family: SPEC
atom_id: AN-S-1251
structure:
  container:
    component: C15
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 13
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Initialize the session engine at host context boundaries

## Claim

### Prose Claim

Each supported agent-host adapter **must** initialize the ANECHOIC session engine at the host's session-start **and** post-compaction boundaries **without** requiring `/ca` invocation.


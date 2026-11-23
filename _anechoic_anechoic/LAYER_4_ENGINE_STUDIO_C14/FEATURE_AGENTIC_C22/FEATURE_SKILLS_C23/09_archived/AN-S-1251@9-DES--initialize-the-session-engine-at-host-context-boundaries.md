---
atom_family: SPEC
atom_id: AN-S-1251
container:
  component: C23
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 11:58:20 +0400
---
## Summary

Initialize the session engine at host context boundaries

# Initialize the session engine at host context boundaries

Each supported agent-host adapter **must** initialize the ANECHOIC session engine at the host's session-start **and** post-compaction boundaries **without** requiring `/ca` invocation.

---
atom_family: SPEC
atom_id: AN-S-4432
container:
  component: C15
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 12:28:12 +0400
---
## Summary

Initialize the session engine at host context boundaries

## Claim



### Prose Claim
Each supported agent-host adapter **must** initialize the ANECHOIC session engine at the host's session-start **and** post-compaction boundaries **without** requiring `/ca` invocation.

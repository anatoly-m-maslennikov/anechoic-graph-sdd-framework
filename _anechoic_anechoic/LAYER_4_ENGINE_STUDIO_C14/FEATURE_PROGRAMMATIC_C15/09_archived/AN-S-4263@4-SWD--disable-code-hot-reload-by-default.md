---
atom_family: SPEC
atom_id: AN-S-4263
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Disable code hot reload by default

## Claim



### Prose Claim
Every code hot-reload mechanism must have an explicit off mode and start disabled by default, including runtime and development launch paths. Enable it only through explicit opt-in. Disabled mode applies code changes through a normal process/container restart and must not keep reload-only child processes or watchers. Source-data indexing is a separate capability; this Policy does not disable Workbench source synchronization.

---
atom_family: SPEC
atom_id: AN-S-1939
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 05:51:23 +0400
---

## Summary

Keep code and compiled schemas fixed at runtime

## Claim

### Prose Claim

Compile schemas, registries and other generated contracts at build time. Load those artifacts at startup and keep them fixed for the life of the process. Apply code or declaration changes by rebuilding and starting the new build. Do not hot reload code or recompile the contracts at runtime. Report missing or invalid build artifacts as errors. Normal source-data synchronization continues under the loaded contracts.

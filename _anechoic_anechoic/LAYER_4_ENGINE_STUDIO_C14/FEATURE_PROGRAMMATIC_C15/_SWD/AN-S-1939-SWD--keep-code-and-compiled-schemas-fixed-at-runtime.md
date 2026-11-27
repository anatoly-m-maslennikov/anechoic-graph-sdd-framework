---
atom_family: SPEC
atom_id: AN-S-1939
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 3
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Keep code and compiled schemas fixed at runtime

## Claim

### Prose Claim

Build and select generated contracts under AN-S-5164. Load those artifacts at startup and keep them fixed for the life of the process. Apply code changes by rebuilding and starting the new build. Do not hot reload code or recompile the contracts at runtime. Report missing or invalid build artifacts as errors. Normal source-data synchronization continues under the loaded contracts.

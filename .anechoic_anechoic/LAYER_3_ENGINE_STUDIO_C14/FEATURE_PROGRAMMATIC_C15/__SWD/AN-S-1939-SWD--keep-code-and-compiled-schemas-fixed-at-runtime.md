---
atom_family: SPEC
atom_id: AN-S-1939
structure:
  container:
    component: C15
  tier: 2
context:
  lens: SWD
state:
  status: active
  version: 2
  updated_at: '2026-11-12T12:34:22.144821+00:00'
---
## Summary

Keep code and compiled schemas fixed at runtime

## Claim

### Prose Claim

Compile schemas, registries and other generated contracts during build-time asset refresh. Existing-assets builds use the checkout assets. Load those artifacts at startup and keep them fixed for the life of the process. Apply code changes by rebuilding and starting the new build. Refresh assets before rebuilding to apply Declaration changes. Do not hot reload code or recompile the contracts at runtime. Report missing or invalid build artifacts as errors. Normal source-data synchronization continues under the loaded contracts.

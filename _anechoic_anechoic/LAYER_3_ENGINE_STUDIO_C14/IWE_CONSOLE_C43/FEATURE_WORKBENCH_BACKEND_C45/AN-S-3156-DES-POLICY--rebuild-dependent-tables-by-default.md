---
atom_family: SPEC
atom_id: AN-S-3156
container:
  component: C45
tier: 1
context:
  template: POLICY
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-20T16:34:57.901983+00:00'
---
## Summary

Rebuild dependent tables by default

## Claim

### Prose Claim

A Workbench table rebuild includes its dependent tables by default. Build them from the same input state, and publish affected views and graph registration with the rebuilt tables.

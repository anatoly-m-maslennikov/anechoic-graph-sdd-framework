---
atom_family: TKT
atom_id: AN-T-2054
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-20T20:35:37.539389+00:00'
---
## Summary

Health observations discard lifecycle failure status

## Claim

### Prose Claim

CA-R-2446@4 and CA-E-640@15 require truthful Tool health observations. The lifecycle provider returns `status`, while `FEATURE_MCP/health_observations.py` examines `outcome`. A local probe with `status: failed` produced an observation of `returned` with outcome `unknown` and no failure category.

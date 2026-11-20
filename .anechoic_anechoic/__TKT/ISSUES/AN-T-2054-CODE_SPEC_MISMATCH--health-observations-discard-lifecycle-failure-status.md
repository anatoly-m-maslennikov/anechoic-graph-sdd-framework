---
identity:
  atom_id: AN-T-2054
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:42.593828+00:00'
---
## Summary

Health observations discard lifecycle failure status

## Claim

### Prose Claim

CA-R-2446@4 and CA-E-640@15 require truthful Tool health observations. The lifecycle provider returns `status`, while `FEATURE_MCP/health_observations.py` examines `outcome`. A local probe with `status: failed` produced an observation of `returned` with outcome `unknown` and no failure category.

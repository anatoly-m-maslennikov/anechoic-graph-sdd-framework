---
atom_family: SPEC
atom_id: AN-S-1311
structure:
  container:
    component: C15
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Evaluate interruption and recovery boundaries

## Claim

### Prose Claim

Interrupt file replacement after temporary output and before final replacement. Accept only explicit authoritative state, recovery limit/retry behavior and diagnostics with no unexplained partial carrier, lock, process or task; otherwise reject the effect boundary.

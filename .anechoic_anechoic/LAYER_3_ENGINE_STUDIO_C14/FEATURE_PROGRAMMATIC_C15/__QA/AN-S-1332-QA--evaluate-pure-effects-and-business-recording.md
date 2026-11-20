---
atom_family: SPEC
atom_id: AN-S-1332
structure:
  container:
    component: C15
  tier: 6
context:
  lens: QA
state:
  status: active
  version: 17
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Evaluate pure effects and business recording

## Claim

### Prose Claim

Pure computations have no hidden I/O/event emission; explicit effects belong to owners with target, precondition and completion fact. Technical diagnostics use stdout/stderr, business lifecycle records use Journal, preflight invents no Run, and record-sink failure is reported independently of applied effect.

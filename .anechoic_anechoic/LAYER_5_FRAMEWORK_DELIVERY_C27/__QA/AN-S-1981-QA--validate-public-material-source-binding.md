---
atom_family: SPEC
atom_id: AN-S-1981
structure:
  container:
    component: C27
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 19
  updated_at: '2026-11-12T17:10:08.584172+00:00'
---
## Summary

Validate public material source binding

## Claim scope

one selected public documentation closure.

## Claim

### Prose Claim

Verify the README, full PR body, Version History and selected Version are the exact prepared public materials that were tested. The PR body has `New` and `Fixed` sections. The newest Version is first in Version History and has the actual matching PR URL. Reject substituted bytes, a different Version or PR, and a guessed link.

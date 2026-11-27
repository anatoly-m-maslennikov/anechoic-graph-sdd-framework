---
atom_family: SPEC
atom_id: AN-S-3350
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-26T16:38:46.252917+00:00'
---

## Summary

Report silent actions and discarded results

## Claim

### Prose Claim

Report a reached path with zero tracked writes and zero observable outputs.
Count a callee return when it reaches the action boundary. Keep declared no-
ops distinct.

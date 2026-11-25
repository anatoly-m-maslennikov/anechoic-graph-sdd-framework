---
atom_family: SPEC
atom_id: AN-S-3349
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Report hidden state effects against declared policies

## Claim

### Prose Claim

Check witnessed reads and writes against the owning state policy and the
purity of reached callers. Keep the input and effect location for each
confirmed violation.

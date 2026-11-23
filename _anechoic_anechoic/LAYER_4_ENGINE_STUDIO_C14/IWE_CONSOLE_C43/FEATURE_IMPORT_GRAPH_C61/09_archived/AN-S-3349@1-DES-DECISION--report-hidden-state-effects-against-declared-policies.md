---
atom_family: SPEC
atom_id: AN-S-3349
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-S-3188@1-draft
  - AN-T-2989@1
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T18:38:16.531857+00:00'
---

## Summary

Report hidden state effects against declared policies

## Claim

### Prose Claim

Check witnessed reads and writes against the owning state policy and the
purity of reached callers. Keep the input and effect location for each
confirmed violation.

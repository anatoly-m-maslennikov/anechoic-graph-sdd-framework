---
atom_family: SPEC
atom_id: AN-S-3350
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3187@1-draft
  - AN-T-2989@1
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T18:38:16.535940+00:00'
---

## Summary

Report silent actions and discarded results

## Claim

### Prose Claim

Report a reached path with zero tracked writes and zero observable outputs.
Count a callee return when it reaches the action boundary. Keep declared no-
ops distinct.

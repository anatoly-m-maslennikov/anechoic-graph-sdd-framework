---
atom_family: SPEC
atom_id: AN-S-3356
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3083@6
  - AN-S-3187@1-draft
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T18:38:16.557010+00:00'
---

## Summary

Report JavaScript import time effects and initialization cycles

## Claim

### Prose Claim

Report witnessed effects during Module evaluation and cycles with an order-
dependent binding read. Apply the selected CommonJS or ESM loader rules and
report source locations.

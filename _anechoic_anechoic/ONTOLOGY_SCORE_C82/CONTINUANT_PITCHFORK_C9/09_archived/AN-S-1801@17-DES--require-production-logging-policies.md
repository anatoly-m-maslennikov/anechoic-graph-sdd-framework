---
atom_family: SPEC
atom_id: AN-S-1801
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 17
  updated_at: "2026-11-25T22:40:52.480794+00:00"
---
## Summary

Require production Logging Policies

## Claim

### Prose Claim


production-relevant components **and** their Logging Policies.


**every** production-relevant component **must** define a Logging Policy. that policy:

- governs required log coverage, structure, severity, safety, **and** retention **before** failures occur;
- supports its Evaluation Controls;
- is referenced by the Catalog Projection over its applicable Evaluation Control Atoms; **and**
- identifies the events **and** context required **to** understand normal operation, detect failure, correlate distributed work, **and** investigate real production issues.

## Details

the policy describes the evaluation boundary, while logger Implementation **and** emitted record Carriers realize it.

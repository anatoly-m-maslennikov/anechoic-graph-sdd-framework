---
atom_family: SPEC
atom_id: AN-S-1207
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 14
  updated_at: "2026-11-25T22:40:48.979340+00:00"
---
## Summary

Bound high-frequency INFO logging

## Claim

### Prose Claim


logging Implementation for high-frequency success, polling, **and** progress events under production Logging Policies.


logging Implementation **must** bound high-frequency success, polling, **and** progress events through aggregation, sampling, **or** emission as `DEBUG` **where** appropriate rather than creating unbounded `INFO` noise.

## Details

the alternatives bound repeated normal-event volume; the severity taxonomy separately classifies material operational milestones.

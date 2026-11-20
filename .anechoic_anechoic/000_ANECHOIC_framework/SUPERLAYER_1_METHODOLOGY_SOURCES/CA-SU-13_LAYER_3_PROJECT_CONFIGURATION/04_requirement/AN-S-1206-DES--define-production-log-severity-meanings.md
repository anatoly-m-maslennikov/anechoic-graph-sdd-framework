---
identity:
  atom_id: AN-S-1206
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 14
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Define production log severity meanings

## Claim

### Prose Claim


Logging Policies for production-relevant components.


a Logging Policy **must** use these four operational levels:

| Level | Required meaning |
|---|---|
| `ERROR` | an operation failed, correctness **or** availability **may** be affected, **or** explicit retry **or** intervention is required |
| `WARNING` | behavior was unexpected **or** degraded but recovered, fell back, **or** remains within an accepted tolerance |
| `INFO` | a material lifecycle, business, **or** operational milestone occurred, including start, stop, acceptance, state transition, completion, **or** summarized progress |
| `DEBUG` | sanitized internal state **or** decision detail is useful for bounded investigation but is unnecessary during normal production operation |

## Details

the four level meanings are one taxonomy **and** retain one lifecycle as a set.

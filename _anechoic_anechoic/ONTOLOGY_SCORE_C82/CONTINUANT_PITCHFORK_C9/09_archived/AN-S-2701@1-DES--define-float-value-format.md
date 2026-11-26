---
atom_family: SPEC
atom_id: AN-S-2701
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 07:51:40 +0400
---
## Summary

Define float Value Format

## Claim

The float Value Format admits floating-point numeric values. It does not set
precision, a numeric range, cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
Format/float.Data Type: float
```

## Semantics

float is the value domain selected by a `[float]` annotation on one direct
property value.

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
  version: 7
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Define float Value Format

## Claim

### Prose Claim


The float Value Format admits floating-point numeric values. It does not set
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```CFEL
# model
CFEL <+ Format/float;

Format/float ((NARROWER_THAN)) Format;
```

## Semantics

float is the value domain selected by a `[float]` annotation on one direct
Property value.

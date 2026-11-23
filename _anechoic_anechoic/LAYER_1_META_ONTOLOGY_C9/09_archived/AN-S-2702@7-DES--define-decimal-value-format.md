---
atom_family: SPEC
atom_id: AN-S-2702
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

Define decimal Value Format

## Claim

### Prose Claim


The decimal Value Format admits decimal numeric values. It does not set scale,
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```CFEL
# model
CFEL <+ Format/decimal;

Format/decimal ((NARROWER_THAN)) Format;
```

## Semantics

decimal is the value domain selected by a `[decimal]` annotation on one direct
Property value.

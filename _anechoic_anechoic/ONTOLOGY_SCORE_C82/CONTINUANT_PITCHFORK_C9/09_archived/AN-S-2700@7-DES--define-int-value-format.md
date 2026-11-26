---
atom_family: SPEC
atom_id: AN-S-2700
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

Define int Value Format

## Claim

### Prose Claim


The int Value Format admits integer numeric values with no fractional part. It
does not set a numeric range, cardinality, uniqueness rule, or carrier
representation.



### Formal Claim

```CFEL
# model
CFEL <+ Format/int;

Format/int ((NARROWER_THAN)) Format;
```

## Semantics

int is the value domain selected by an `[int]` annotation on one direct
Property value.

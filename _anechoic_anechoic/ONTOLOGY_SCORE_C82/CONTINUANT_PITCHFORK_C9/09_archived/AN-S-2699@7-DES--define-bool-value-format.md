---
atom_family: SPEC
atom_id: AN-S-2699
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

Define bool Value Format

## Claim

### Prose Claim


The bool Value Format admits the Boolean values true and false. It does not set a
property's cardinality, default, nullability, or carrier representation.



### Formal Claim

```CFEL
# model
CFEL <+ Format/bool;

Format/bool ((NARROWER_THAN)) Format;
```

## Semantics

bool is the value domain selected by a `[bool]` annotation on one direct
Property value.

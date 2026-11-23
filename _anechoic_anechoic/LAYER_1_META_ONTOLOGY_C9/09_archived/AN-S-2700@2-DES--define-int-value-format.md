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
  version: 2
  updated_at: 2026-10-29 09:46:50 +0400
---
## Summary

Define int Value Format

## Claim

The int Value Format admits integer numeric values with no fractional part. It
does not set a numeric range, cardinality, uniqueness rule, or carrier
representation.

### Formal claim

```text
Entity/Graph Syntax > Format/int
```

## Semantics

int is the value domain selected by an `[int]` annotation on one direct
property value.

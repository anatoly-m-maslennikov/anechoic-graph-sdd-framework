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
  version: 2
  updated_at: 2026-10-29 09:46:50 +0400
---
## Summary

Define bool Value Format

## Claim

The bool Value Format admits Boolean values: true and false. It does not set a
property's cardinality, default, nullability, or carrier representation.

### Formal claim

```text
Entity/Graph Syntax > Format/bool
```

## Semantics

bool is the value domain selected by a `[bool]` annotation on one direct
property value.

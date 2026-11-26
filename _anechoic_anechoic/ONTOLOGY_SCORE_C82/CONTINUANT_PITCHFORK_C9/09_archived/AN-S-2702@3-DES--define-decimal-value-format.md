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
  version: 3
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define decimal Value Format

## Claim

The decimal Value Format admits decimal numeric values. It does not set scale,
precision, a numeric range, cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
CFEL > Format/decimal
```

## Semantics

decimal is the value domain selected by a `[decimal]` annotation on one direct
property value.

---
atom_family: SPEC
atom_id: AN-S-2704
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

Define datetime Value Format

## Claim

The datetime Value Format admits date-and-time values. It does not set a
timezone convention, precision, cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
Entity/Graph Syntax > Format/datetime
```

## Semantics

datetime is the value domain selected by a `[datetime]` annotation on one
direct property value.

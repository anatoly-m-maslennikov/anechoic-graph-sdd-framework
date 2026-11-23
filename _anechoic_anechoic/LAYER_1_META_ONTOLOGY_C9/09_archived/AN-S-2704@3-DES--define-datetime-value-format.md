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
  version: 3
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define datetime Value Format

## Claim

The datetime Value Format admits date-and-time values. It does not set a
timezone convention, precision, cardinality, uniqueness, or carrier
representation.

### Formal claim

```text
CFEL > Format/datetime
```

## Semantics

datetime is the value domain selected by a `[datetime]` annotation on one
direct property value.

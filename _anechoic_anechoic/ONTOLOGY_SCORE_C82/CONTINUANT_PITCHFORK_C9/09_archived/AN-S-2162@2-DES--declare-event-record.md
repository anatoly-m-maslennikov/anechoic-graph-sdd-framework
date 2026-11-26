---
atom_family: SPEC
atom_id: AN-S-2162
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Declare Event Record

## Claim

An Event Record is immutable.

```CFEL
Event Record {:0}((IS_PROPERTY_OF));
Event Record// {:1}((IS_CONTAINED_BY)) Journal//
```

## Semantics

An Event Record is a persistent description of an event and its recorded evidence.

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
  version: 4
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Declare Event Record

## Claim

### Prose Claim


An Event Record is immutable.


### Formal Claim

```CFEL
# model
Event Record {::0}((IS_PROPERTY_OF));

Event Record ((NARROWER_THAN)) Continuant;

# instances
Event Record//$event_record {::1}((IS_CONTAINED_BY)) Journal//$journal
```

## Semantics

An Event Record is a persistent description of an event and its recorded evidence.

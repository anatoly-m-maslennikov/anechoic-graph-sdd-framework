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
  version: 8
  updated_at: '2026-11-13T05:16:34.014125+00:00'
---
## Summary

Define datetime Value Format

## Claim

### Prose Claim


The datetime Value Format admits date-and-time values. It does not set a
timezone convention, precision, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/datetime',))
relation(source='Format/datetime', name='NARROWER_THAN', target='Format')
```

## Semantics

datetime is the value domain selected by a `[datetime]` annotation on one
direct Property value.

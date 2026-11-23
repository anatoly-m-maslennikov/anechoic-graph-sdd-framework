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
  version: 8
  updated_at: '2026-11-13T05:16:23.243806+00:00'
---
## Summary

Define decimal Value Format

## Claim

### Prose Claim


The decimal Value Format admits decimal numeric values. It does not set scale,
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/decimal',))
relation(source='Format/decimal', name='NARROWER_THAN', target='Format')
```

## Semantics

decimal is the value domain selected by a `[decimal]` annotation on one direct
Property value.

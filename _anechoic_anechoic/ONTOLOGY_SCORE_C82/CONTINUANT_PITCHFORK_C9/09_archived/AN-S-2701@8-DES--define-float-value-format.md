---
atom_family: SPEC
atom_id: AN-S-2701
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-13T05:16:19.063289+00:00'
---
## Summary

Define float Value Format

## Claim

### Prose Claim


The float Value Format admits floating-point numeric values. It does not set
precision, a numeric range, cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/float',))
relation(source='Format/float', name='NARROWER_THAN', target='Format')
```

## Semantics

float is the value domain selected by a `[float]` annotation on one direct
Property value.

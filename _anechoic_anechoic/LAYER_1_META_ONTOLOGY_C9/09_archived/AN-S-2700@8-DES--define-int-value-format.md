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
  version: 8
  updated_at: '2026-11-13T05:16:16.568884+00:00'
---
## Summary

Define int Value Format

## Claim

### Prose Claim


The int Value Format admits integer numeric values with no fractional part. It
does not set a numeric range, cardinality, uniqueness rule, or carrier
representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/int',))
relation(source='Format/int', name='NARROWER_THAN', target='Format')
```

## Semantics

int is the value domain selected by an `[int]` annotation on one direct
Property value.

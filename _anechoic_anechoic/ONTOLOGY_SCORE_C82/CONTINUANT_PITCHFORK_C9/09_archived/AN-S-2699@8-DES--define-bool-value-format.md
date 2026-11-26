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
  version: 8
  updated_at: '2026-11-13T05:16:13.736930+00:00'
---
## Summary

Define bool Value Format

## Claim

### Prose Claim


The bool Value Format admits the Boolean values true and false. It does not set a
property's cardinality, default, nullability, or carrier representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/bool',))
relation(source='Format/bool', name='NARROWER_THAN', target='Format')
```

## Semantics

bool is the value domain selected by a `[bool]` annotation on one direct
Property value.

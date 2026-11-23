---
atom_family: SPEC
atom_id: AN-S-2703
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: '2026-11-13T05:16:28.353595+00:00'
---
## Summary

Define string Value Format

## Claim

### Prose Claim


The string Value Format admits textual string values. It does not turn null
into a string or set a property's cardinality, uniqueness, or carrier
representation.



### Formal Claim

```python
# model
composition(container='CFEL', parts=('Format/string',))
relation(source='Format/string', name='NARROWER_THAN', target='Format')
```

## Semantics

string is the value domain selected by a `[string]` annotation on one direct
Property value.

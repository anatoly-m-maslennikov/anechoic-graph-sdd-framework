---
atom_family: SPEC
atom_id: AN-S-2225
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:57:01.775034+00:00"
---

## Summary

Declare CFEL Relation endpoint signature

## Claim

### Formal Claim

```python
# model
set_value(address='Operator//RelationEndpointSignature', value='"$host ((RELATION)) $target"')
```

## Semantics

Within a Relation Declaration Formal Claim only, `$host` and `$target`
range over declared model entities or instances, including Carrier and CFEL,
and exclude literals. The signature creates neither a Relation fact nor
instance data. Known endpoint kinds remain typed selectors; this does not extend
untyped variables to other CFEL contexts.

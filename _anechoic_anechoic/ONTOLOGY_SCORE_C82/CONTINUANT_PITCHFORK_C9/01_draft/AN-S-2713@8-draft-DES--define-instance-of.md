---
atom_family: SPEC
atom_id: AN-S-2713
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 8
  updated_at: '2026-11-13T08:33:34.755021+00:00'
---
## Summary

Define INSTANCE_OF

## Claim

### Prose Claim

The Host is an instance of the Target declared kind. A Property instance is borne by its data bearer and is an instance of its corresponding model Property, which remains borne by its model bearer. A Property instance has no independent Carrier; its bearer and kind Relations are distinct and may coexist.

Forward `Host ((INSTANCE_OF)) Target` and reverse `Target <((INSTANCE_OF)) Host` are views of the same Relation fact.
In `X//Y`, Y INSTANCE_OF X; traversal runs from kind to instance.
INSTANCE_OF relates instance of a declared kind to declared kind.
### Formal Claim

```python
# model
relation(source='Relation//INSTANCE_OF', name='HAS_INVERSE', target='Relation//HAS_INSTANCE')
set_value(address='alias(Relation//INSTANCE_OF)', value='"//"')
classify(address='Relation//INSTANCE_OF', axis='Derivation', value='Direct', notation='relation')
# instances
relation(source='$instance', name='INSTANCE_OF', target='$kind')
```


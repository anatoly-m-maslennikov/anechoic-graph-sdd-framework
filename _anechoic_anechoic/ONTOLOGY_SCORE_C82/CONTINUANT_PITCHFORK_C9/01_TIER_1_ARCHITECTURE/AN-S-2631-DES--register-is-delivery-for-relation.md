---
atom_family: SPEC
atom_id: AN-S-2631
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 32
  updated_at: "2026-11-24T23:26:21.193827+00:00"
---
## Summary

Register IS_DELIVERY_FOR relation

## Claim

### Prose Claim

#### Applicability
`IS_DELIVERY_FOR` relations.

`IS_DELIVERY_FOR` **means** the direct relation from a Delivery Atom to the Atom
that the Delivery realizes.

Forward `Host ((IS_DELIVERY_FOR)) Target` and reverse `Target <((IS_DELIVERY_FOR)) Host` are views of the same Relation fact.
IS_DELIVERY_FOR relates Delivery Atom to realized Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_DELIVERY_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Delivery)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

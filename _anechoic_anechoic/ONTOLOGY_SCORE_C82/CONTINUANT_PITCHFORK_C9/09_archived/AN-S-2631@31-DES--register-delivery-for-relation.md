---
atom_family: SPEC
atom_id: AN-S-2631
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 31
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Register delivery_for relation

## Claim

### Prose Claim

#### Applicability
`delivery_for` relations.

`delivery_for` **means** the direct relation from a Delivery Atom to the Atom
that the Delivery realizes.

Forward `Host ((delivery_for)) Target` and reverse `Target <((delivery_for)) Host` are views of the same Relation fact.
delivery_for relates Delivery Atom to realized Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='delivery_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Delivery)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```


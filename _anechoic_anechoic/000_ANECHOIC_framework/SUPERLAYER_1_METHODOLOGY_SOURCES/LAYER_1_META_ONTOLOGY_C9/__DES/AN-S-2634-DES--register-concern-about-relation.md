---
atom_family: SPEC
atom_id: AN-S-2634
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 33
  updated_at: '2026-11-12T20:24:07.873527+00:00'
---
## Summary

Register concern_about relation

## Claim

### Prose Claim

#### Applicability
`concern_about` relations.

`concern_about` **means** the direct relation from a Concern Atom to the
governed entity that it concerns.

The Host is a Concern Atom; the governed target is the Entity concerned.
Forward `Host ((concern_about)) Target` and reverse `Target <((concern_about)) Host` are views of the same Relation fact.
concern_about relates Concern Atom to governed entity concerned.

#### Details
Endpoint admission is an Atom Entity Definition concern, not Relation Definition
metadata.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='concern_about',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Concern)',)},
    target_endpoint={'level': 'model_entities_or_instances'},
)
```


---
atom_family: SPEC
atom_id: AN-S-2634
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 34
  updated_at: "2026-11-25T22:50:35.910045+00:00"
---
## Summary

Register CONCERNS relation

## Claim

### Prose Claim

#### Applicability
`CONCERNS` relations.

`CONCERNS` **means** the direct relation from a Concern Atom to the
governed entity that it concerns.

The Host is a Concern Atom; the governed target is the Entity concerned.
Forward `Host ((CONCERNS)) Target` and reverse `Target <((CONCERNS)) Host` are views of the same Relation fact.
CONCERNS relates Concern Atom to governed entity concerned.

#### Details
Endpoint admission is an Atom Entity Definition concern, not Relation Definition
metadata.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CONCERNS',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Concern)',)},
    target_endpoint={'level': 'model_entities_or_instances'},
)
```

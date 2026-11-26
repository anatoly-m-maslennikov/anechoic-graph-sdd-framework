---
atom_family: SPEC
atom_id: AN-S-2628
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 35
  updated_at: "2026-11-25T22:50:34.885433+00:00"
---
## Summary

Register IS_RATIONALE_FOR relation

## Claim

### Prose Claim

#### Applicability
Rationale For Relation.

`IS_RATIONALE_FOR` **means** the direct relation from a Rationale Analysis and Advisory Atom
to the Atom that it explains.

Forward `Host ((IS_RATIONALE_FOR)) Target` and reverse `Target <((IS_RATIONALE_FOR)) Host` are views of the same Relation fact.
IS_RATIONALE_FOR relates Rationale Analysis and Advisory Atom to explained Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_RATIONALE_FOR',
    source_endpoint={'level': 'instances',
 'entity_paths': ('Atom/(.Header.Context.Role := Analysis and '
                  'Advisory)/(.Header.Context.Form := Rationale)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

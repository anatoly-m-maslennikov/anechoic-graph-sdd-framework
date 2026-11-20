---
identity:
  atom_id: AN-S-2628
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 34
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Register rationale_for relation

## Claim

### Prose Claim

#### Applicability
Rationale For Relation.

`rationale_for` **means** the direct relation from a Rationale Analysis and Advisory Atom
to the Atom that it explains.

Forward `Host ((rationale_for)) Target` and reverse `Target <((rationale_for)) Host` are views of the same Relation fact.
rationale_for relates Rationale Analysis and Advisory Atom to explained Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='rationale_for',
    source_endpoint={'level': 'instances',
 'entity_paths': ('Atom/(.Header.Context.Role := Analysis and '
                  'Advisory)/(.Header.Context.Form := Rationale)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```


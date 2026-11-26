---
atom_family: SPEC
atom_id: AN-S-2630
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 39
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Register Evaluation targets

## Claim

### Prose Claim

#### Applicability
direct `evaluation_for` relations.

`evaluation_for` **means** the direct relation from an Evaluation Atom to an
Atom whose authority the Evaluation checks.

Forward `Host ((evaluation_for)) Target` and reverse `Target <((evaluation_for)) Host` are views of the same Relation fact.
evaluation_for relates Evaluation Atom to Atom whose authority is evaluated.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='evaluation_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Evaluation)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```


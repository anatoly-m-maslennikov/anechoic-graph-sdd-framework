---
atom_family: SPEC
atom_id: AN-S-2629
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 32
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Register method_for relation

## Claim

### Prose Claim

#### Applicability
Method For Relation.

`method_for` **means** the direct relation from a Method Atom to the
Requirement Atom that the Method serves.

Forward `Host ((method_for)) Target` and reverse `Target <((method_for)) Host` are views of the same Relation fact.
method_for relates Method Atom to served Requirement Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='method_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Method)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Requirement)',)},
)
```


---
atom_family: SPEC
atom_id: AN-S-2629
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 33
  updated_at: "2026-11-24T23:26:21.103383+00:00"
---
## Summary

Register IS_METHOD_FOR relation

## Claim

### Prose Claim

#### Applicability
Method For Relation.

`IS_METHOD_FOR` **means** the direct relation from a Method Atom to the
Requirement Atom that the Method serves.

Forward `Host ((IS_METHOD_FOR)) Target` and reverse `Target <((IS_METHOD_FOR)) Host` are views of the same Relation fact.
IS_METHOD_FOR relates Method Atom to served Requirement Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_METHOD_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Method)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Requirement)',)},
)
```

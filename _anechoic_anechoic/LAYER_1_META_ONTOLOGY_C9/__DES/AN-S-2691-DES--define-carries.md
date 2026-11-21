---
atom_family: SPEC
atom_id: AN-S-2691
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Define CARRIES

## Claim

### Prose Claim

#### Claim scope
Carrier bindings of non-ephemeral Entities.

CARRIES **means** the directed Relation from a Carrier **to** the non-ephemeral Entity that it stores **or** represents.

The Target is the non-ephemeral Entity stored or represented by the Carrier.
Forward `Host ((CARRIES)) Target` and reverse `Target <((CARRIES)) Host` are views of the same Relation fact.
CARRIES relates Carrier to non-ephemeral Entity.

#### Details
IS_CARRIED_BY **means** the inverse of CARRIES, directed from a non-ephemeral Entity to its Carrier. The Carrier binding exposes this inverse direction; it is not a separately authored primitive Relation fact. This preserves the existing meaning defined by CA-D-257. Neither direction requires a separately registered binding for each YAML field or Markdown section, a new Carrier, a snapshot or a historical record. The applicable D policy specifies how the represented Entity is bound and represented. No additional endpoint class, graph ownership, cardinality or inference permission is introduced by moving this definition to R.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CARRIES',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'ephemeral': False},
    inverse_alias='IS_CARRIED_BY',
)
```


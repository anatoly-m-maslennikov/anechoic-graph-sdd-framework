---
atom_family: SPEC
atom_id: AN-S-2735
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 47
  updated_at: "2026-11-26T16:35:54.500403+00:00"
---
## Summary

Keep tier-parent relations within Atom Scope

## Claim

### Prose Claim

#### Applicability
The existing governing IS_TIER_GOVERNED_BY relation, pending its separately planned replacement.

IS_TIER_GOVERNED_BY is the directed governing connection from a child Atom to the parent Atom whose Claim governs that child's contribution. It is distinct from containment, dependency, classification and source-layer membership. The Atom definition CA-R-2508 governs endpoint admission for legacy sources. Interpret their existing order under the archived AN-S-1684@15. Current Relation Manifests govern native edges.

Forward `Host ((IS_TIER_GOVERNED_BY)) Target` and reverse `Target <((IS_TIER_GOVERNED_BY)) Host` are views of the same Relation fact.
IS_TIER_GOVERNED_BY relates child Atom to parent Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_TIER_GOVERNED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

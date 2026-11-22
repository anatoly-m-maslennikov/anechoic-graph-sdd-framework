---
atom_family: SPEC
atom_id: AN-S-2652
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 39
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define GOVERNS Subject Relation Kind

## Claim

### Prose Claim

#### Applicability
the GOVERNS Subject Relation Kind.

GOVERNS **means** the direct Subject Relation Kind from an Atom **to** the canonical Subject entity or instance about which the Atom governs through its applicable role-specific content.

The Target is the canonical Subject about which the Atom governs through its applicable content.
Forward `Host ((GOVERNS)) Target` and reverse `Target <((GOVERNS)) Host` are views of the same Relation fact.
GOVERNS relates Atom to canonical Subject entity or instance.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='GOVERNS',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'model_entities_or_instances'},
)
```


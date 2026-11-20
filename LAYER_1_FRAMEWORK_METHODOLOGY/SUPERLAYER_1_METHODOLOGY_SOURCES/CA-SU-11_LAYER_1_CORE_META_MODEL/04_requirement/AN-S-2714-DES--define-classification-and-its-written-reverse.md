---
identity:
  atom_id: AN-S-2714
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Define classification and its written reverse

## Claim

### Prose Claim

HAS_CLASSIFICATION relates a declared Entity or instance to an applicable classification axis. `Entity >| Axis` and `Axis |< Entity` are opposite written views of the same fact. An axis is distinct from its value case.

The Target is an applicable classification axis; the classified Entity may be a Relation or another declared Entity.

Forward `Host ((HAS_CLASSIFICATION)) Target` and reverse `Target <((HAS_CLASSIFICATION)) Host` are views of the same Relation fact.
HAS_CLASSIFICATION relates declared Entity or instance to applicable classification axis.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_CLASSIFICATION',
    source_endpoint={'level': 'model_entities_or_instances'},
    target_endpoint={'level': 'model_entities', 'classification_axis': True},
    written_alias='>|',
    reverse_written_alias='|<',
)
```


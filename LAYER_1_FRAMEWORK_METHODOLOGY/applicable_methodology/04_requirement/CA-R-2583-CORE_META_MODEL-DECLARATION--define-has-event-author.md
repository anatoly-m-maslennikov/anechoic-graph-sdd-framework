---
atom_id: CA-R-2583
ref_id: CA-R-2583
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//HAS_EVENT_AUTHOR
tier: 3
status: active
version: 6
updated_at: '2026-11-13T22:36:47.668532+00:00'
carrier_destination:
  file:
    name: CA-R-2583-CORE_META_MODEL-DECLARATION--define-has-event-author.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2583-CORE_META_MODEL-DECLARATION--define-has-event-author.md
  source_atom_id: CA-R-2583
  source_atom_revision: 6
  source_sha256: f1bad067587e03c71c8b9401aaebada05c7b097b8b630e12e390d177c48450b7
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define HAS_EVENT_AUTHOR

## Claim

### Prose Claim

HAS_EVENT_AUTHOR identifies the Actor who performed the recorded event.

Forward `Host ((HAS_EVENT_AUTHOR)) Target` and reverse `Target <((HAS_EVENT_AUTHOR)) Host` are views of the same Relation fact.
HAS_EVENT_AUTHOR relates Event Record instance to Actor instance.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_EVENT_AUTHOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Event Record',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Actor',)},
    inverse_alias='IS_EVENT_AUTHOR_OF',
)
```


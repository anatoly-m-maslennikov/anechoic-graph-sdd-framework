---
atom_id: CA-R-1019
ref_id: CA-R-1019
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//delivery_for
  dependencies:
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: active
version: 31
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-1019-CORE_META_MODEL-DECLARATION--register-delivery-for-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1019-CORE_META_MODEL-DECLARATION--register-delivery-for-relation.md
  source_atom_id: CA-R-1019
  source_atom_revision: 31
  source_sha256: e16a3db01c4591739bc3d773ba4704cc463bc921dc11b5405ac3ccab9ca91044
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register delivery_for relation

## Claim

### Prose Claim

#### Applicability
`delivery_for` relations.

`delivery_for` **means** the direct relation from a Delivery Atom to the Atom
that the Delivery realizes.

Forward `Host ((delivery_for)) Target` and reverse `Target <((delivery_for)) Host` are views of the same Relation fact.
delivery_for relates Delivery Atom to realized Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='delivery_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Delivery)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```


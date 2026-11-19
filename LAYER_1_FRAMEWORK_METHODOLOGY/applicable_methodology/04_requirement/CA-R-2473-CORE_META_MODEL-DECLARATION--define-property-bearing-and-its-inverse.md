---
atom_id: CA-R-2473
ref_id: CA-R-2473
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//IS_PROPERTY_OF
tier: 3
status: active
version: 8
updated_at: '2026-11-14T07:32:51.119753+00:00'
carrier_destination:
  file:
    name: CA-R-2473-CORE_META_MODEL-DECLARATION--define-property-bearing-and-its-inverse.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2473-CORE_META_MODEL-DECLARATION--define-property-bearing-and-its-inverse.md
  source_atom_id: CA-R-2473
  source_atom_revision: 8
  source_sha256: c2f506daba0357367e8ea889ad41a81dc6c206ecc4ce1170c4730d348674aaea
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Property bearing and its inverse

## Claim

### Prose Claim

IS_PROPERTY_OF directs a Property to its immediate bearer. HAS_PROPERTY is its derived inverse. `Bearer.Property` addresses the Property.

Forward `Host ((IS_PROPERTY_OF)) Target` and reverse `Target <((IS_PROPERTY_OF)) Host` are views of the same Relation fact.
In `X.Y`, Y IS_PROPERTY_OF X; traversal runs from bearer to Property.
IS_PROPERTY_OF relates Property to immediate bearer.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_PROPERTY_OF',
    endpoint_pairs=(
        {
            'source_endpoint': {'level': 'model_entities', 'dependency': 'property'},
            'target_endpoint': {'level': 'model_entities'},
        },
        {
            'source_endpoint': {'level': 'instances', 'dependency': 'property'},
            'target_endpoint': {'level': 'instances'},
        },
    ),
    inverse_alias='HAS_PROPERTY',
    written_alias='.',
)
```

---
atom_id: CA-R-2741
ref_id: CA-R-2741
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Projection/(.Form := Primary Entities with Direct
    Properties)
tier: 3
status: active
version: 3
updated_at: '2026-11-12T18:49:25.879498+00:00'
carrier_destination:
  file:
    name: CA-R-2741-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-with-direct-properties.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2741-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-with-direct-properties.md
  source_atom_id: CA-R-2741
  source_atom_revision: 3
  source_sha256: 3b26902b6a9eaae4e8b09a83b5392e65bcafcefa87fe2cd2a296f44a8c3fc946
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection/(.Form := Primary Entities with Direct Properties)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class PrimaryEntitiesWithDirectProperties(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesWithDirectProperties, entity_name='Primary Entities with Direct Properties', qualification_property_path="Projection.Form")
```

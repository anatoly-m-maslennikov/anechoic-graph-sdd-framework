---
atom_id: CA-R-2738
ref_id: CA-R-2738
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Projection/(.Form := Map)
tier: 3
status: active
version: 3
updated_at: '2026-11-12T18:49:18.400336+00:00'
carrier_destination:
  file:
    name: CA-R-2738-CORE_META_MODEL-DECLARATION--declare-projection-form-map.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2738-CORE_META_MODEL-DECLARATION--declare-projection-form-map.md
  source_atom_id: CA-R-2738
  source_atom_revision: 3
  source_sha256: 6adf8b15be5bf569f9e28a1fddaa3b36345a9e248dfa94bb6aad6935e628ce1a
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection/(.Form := Map)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Map(Projection):
    pass

declare_entity(entity_class=Map, entity_name='Map', qualification_property_path="Projection.Form")
```

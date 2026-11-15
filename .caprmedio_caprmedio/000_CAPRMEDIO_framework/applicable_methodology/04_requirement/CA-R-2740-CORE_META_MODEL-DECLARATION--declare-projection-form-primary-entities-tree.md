---
atom_id: CA-R-2740
ref_id: CA-R-2740
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection/(.Form := Primary Entities Tree)
tier: 3
status: active
version: 3
updated_at: '2026-11-12T18:49:23.370786+00:00'
carrier_destination:
  file:
    name: CA-R-2740-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-tree.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2740-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-tree.md
  source_atom_id: CA-R-2740
  source_atom_revision: 3
  source_sha256: 5d33c9f22d1d11daaa9eb1532602fbe939fe2211f09a527d8c892fd48ad0bd8b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection/(.Form := Primary Entities Tree)

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Projection

class PrimaryEntitiesTree(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesTree, entity_name='Primary Entities Tree', qualification_property_path="Projection.Form")
```

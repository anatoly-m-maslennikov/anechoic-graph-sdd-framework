---
atom_id: CA-R-2742
ref_id: CA-R-2742
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Projection/(.Form := Primary Entities with Inherited
    Property Contracts)
tier: 3
status: active
version: 3
updated_at: '2026-11-12T18:49:28.329068+00:00'
carrier_destination:
  file:
    name: CA-R-2742-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-with-inherited-property-contracts.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2742-CORE_META_MODEL-DECLARATION--declare-projection-form-primary-entities-with-inherited-property-contracts.md
  source_atom_id: CA-R-2742
  source_atom_revision: 3
  source_sha256: 20557f4404b672b164a5892f182d2fd03cbf166a687c29f51fb597c75813cd13
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Projection/(.Form := Primary Entities with Inherited Property Contracts)

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Projection

class PrimaryEntitiesWithInheritedPropertyContracts(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesWithInheritedPropertyContracts, entity_name='Primary Entities with Inherited Property Contracts', qualification_property_path="Projection.Form")
```

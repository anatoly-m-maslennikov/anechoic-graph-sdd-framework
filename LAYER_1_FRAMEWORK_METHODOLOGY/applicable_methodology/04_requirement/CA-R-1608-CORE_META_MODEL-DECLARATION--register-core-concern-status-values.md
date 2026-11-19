---
atom_id: CA-R-1608
ref_id: CA-R-1608
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Concern).Header.State.Status
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Concern)
  - ANECHOIC_MODEL <+ Atom.Header.State.Status
tier: 2
status: active
version: 24
updated_at: '2026-11-12T19:34:36.593311+00:00'
carrier_destination:
  file:
    name: CA-R-1608-CORE_META_MODEL-DECLARATION--register-core-concern-status-values.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1608-CORE_META_MODEL-DECLARATION--register-core-concern-status-values.md
  source_atom_id: CA-R-1608
  source_atom_revision: 24
  source_sha256: 2c9d00e943ba2a656dddc11fb69ea6348ee173db6fd933855fc7bce40ea8aed6
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register Core Concern Status Values

## Claim

### Prose Claim


the Core Concern Status model.


the Core Concern Status model **must** inherit the allowed values of Atom.Header.Status and add (Resolved, Canceled).

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

declare_entity(
    entity_name='Status',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.State',
    allowed_values=('Resolved', 'Canceled'),
    status_order_numbers={'Resolved': 21},
    applies_to_entity_classes=(Concern,),
)
```

---
atom_id: CA-R-2498
ref_id: CA-R-2498
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Content
tier: 3
status: active
version: 7
updated_at: '2026-11-13T01:11:40.238494+00:00'
carrier_destination:
  file:
    name: CA-R-2498-CORE_META_MODEL-DECLARATION--declare-atom-content.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2498-CORE_META_MODEL-DECLARATION--declare-atom-content.md
  source_atom_id: CA-R-2498
  source_atom_revision: 7
  source_sha256: 1b11e18bf2d9ab31687b562abb2c3d3e270194393af7c8a2e7b6fc960024ad8f
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom.Content

## Claim

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Requirement, Method, Evaluation, Delivery
declare_entity(entity_name="Content", relation_name="IS_PROPERTY_OF", base_path="Atom",
    property_occurrence_cardinality=1, value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None), dependent_property_name_format=str,
    recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    recursive_dependent_property_name_format=str, recursive_dependent_property_value_format="markdown",
    ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),
    ordered_dependent_property_pairs=(("Summary", "Claim"), ("Claim", "Semantics"), ("Semantics", "Details")))
```
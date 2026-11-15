---
atom_id: CA-R-2500
ref_id: CA-R-2500
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Content.Claim
tier: 3
status: active
version: 8
updated_at: '2026-11-13T00:27:09.632965+00:00'
carrier_destination:
  file:
    name: CA-R-2500-CORE_META_MODEL-DECLARATION--declare-atom-content-claim.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2500-CORE_META_MODEL-DECLARATION--declare-atom-content-claim.md
  source_atom_id: CA-R-2500
  source_atom_revision: 8
  source_sha256: 033f4f93b5ec64953f32ad2c1f196713a326a2be7a1b90de611971afd78280bd
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom.Content.Claim

## Claim

### Prose Claim

A complete ordinary RMED Claim has at least one of Formal Claim and Prose Claim. Sibling names are unique. Formal Claim uses the fenced language admitted by its declaration. Prose Claim contains ordinary Markdown. A Markdown heading inside Prose Claim is part of its value, unless an applicable declaration expressly declares it as a child Property.

### Formal Claim

```python
from caprmedio.formal_claims import Cardinality, declare_entity
from caprmedio.model import Requirement, Method, Evaluation, Delivery

declare_entity(entity_name="Claim", relation_name="IS_PROPERTY_OF", base_path="Atom.Content", property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=Cardinality(minimum=1, maximum=2), dependent_property_name_format=str, allowed_dependent_property_names=("Formal Claim", "Prose Claim"), ordered_dependent_property_pairs=(("Prose Claim", "Formal Claim"),), applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery))
```

---
atom_id: CA-R-2722
ref_id: CA-R-2722
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Content.Claim.Prose Claim
tier: 3
status: active
version: 5
updated_at: '2026-11-12T19:13:08.274065+00:00'
carrier_destination:
  file:
    name: CA-R-2722-CORE_META_MODEL-DECLARATION--declare-atom-content-claim-prose-claim.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2722-CORE_META_MODEL-DECLARATION--declare-atom-content-claim-prose-claim.md
  source_atom_id: CA-R-2722
  source_atom_revision: 5
  source_sha256: 9a027ddd8fd3451036df471277d420fcc821d32d9ca72be21f91ba660328337c
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom.Content.Claim.Prose Claim

## Claim

### Prose Claim

Prose Claim is a child Property of Claim. Its value is ordinary Markdown; headings within that value are not Properties unless an applicable declaration admits them.
### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery

declare_entity(
    entity_name="Prose Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Content.Claim",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
    applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery),
)
```

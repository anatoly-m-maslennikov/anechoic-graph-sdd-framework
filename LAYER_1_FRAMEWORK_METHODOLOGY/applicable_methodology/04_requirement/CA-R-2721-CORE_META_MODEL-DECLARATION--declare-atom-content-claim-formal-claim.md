---
atom_id: CA-R-2721
ref_id: CA-R-2721
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Content.Claim.Formal Claim
tier: 3
status: active
version: 6
updated_at: '2026-11-12T23:58:44.705301+00:00'
carrier_destination:
  file:
    name: CA-R-2721-CORE_META_MODEL-DECLARATION--declare-atom-content-claim-formal-claim.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2721-CORE_META_MODEL-DECLARATION--declare-atom-content-claim-formal-claim.md
  source_atom_id: CA-R-2721
  source_atom_revision: 6
  source_sha256: 28ab146b17dd25e096ad8bb234aafc4036280fbe7d2c4bb309a3e62bd9ad8dc3
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Atom.Content.Claim.Formal Claim

## Claim

### Prose Claim

Formal Claim is a child Property of Claim. Its value contains one fenced formal expression. A Python fence is admitted when the affected consumers support the Python representation for that Claim. CFEL remains admitted during migration.
### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Formal Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Content.Claim",
    applies_to_entity_classes=("Requirement", "Method", "Evaluation", "Delivery"),
    value_format="markdown",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```

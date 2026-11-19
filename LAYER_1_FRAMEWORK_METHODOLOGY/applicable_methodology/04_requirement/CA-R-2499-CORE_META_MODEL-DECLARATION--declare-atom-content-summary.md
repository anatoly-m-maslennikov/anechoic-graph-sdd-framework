---
atom_id: CA-R-2499
ref_id: CA-R-2499
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Content.Summary
tier: 3
status: active
version: 7
updated_at: '2026-11-13T04:04:17.466607+00:00'
carrier_destination:
  file:
    name: CA-R-2499-CORE_META_MODEL-DECLARATION--declare-atom-content-summary.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2499-CORE_META_MODEL-DECLARATION--declare-atom-content-summary.md
  source_atom_id: CA-R-2499
  source_atom_revision: 7
  source_sha256: 92c9fd71daf062e6837808f1896fb17eb3bd85acefe75cf8371a04fefd96ecaa
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom.Content.Summary

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Summary", relation_name="IS_PROPERTY_OF", base_path="Atom.Content",
    property_occurrence_cardinality=1, value_cardinality=1, dependent_property_cardinality=0,
    population_entity_path="Atom",
    population_functional_dependencies=(
        {"keys": ("Header.Identity.ID",), "dependents": ("Content.Summary",),
         "status_groups": ("Current", "Backlog", "Archived")},
    ),
)
```


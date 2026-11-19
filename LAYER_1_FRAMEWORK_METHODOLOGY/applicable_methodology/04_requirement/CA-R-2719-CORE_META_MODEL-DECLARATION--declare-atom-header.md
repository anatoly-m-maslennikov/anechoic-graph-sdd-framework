---
atom_id: CA-R-2719
ref_id: CA-R-2719
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header
tier: 3
status: active
version: 5
updated_at: '2026-11-13T01:11:43.332082+00:00'
carrier_destination:
  file:
    name: CA-R-2719-CORE_META_MODEL-DECLARATION--declare-atom-header.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2719-CORE_META_MODEL-DECLARATION--declare-atom-header.md
  source_atom_id: CA-R-2719
  source_atom_revision: 5
  source_sha256: 6dc2fdc36d5e64fdc343c1f3cd9c662bcc52c0d6e87659e37ad67c31ff97a0f6
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom.Header

## Claim

### Prose Claim

Atom.Header groups the Atom Properties carried in YAML frontmatter, including for Draft Atoms.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Header",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_name_format=str,
    allowed_dependent_property_names=("Identity", "Context", "Relations", "State", "Destination"),
    ordered_dependent_property_pairs=(
        ("Identity", "Context"),
        ("Context", "Relations"),
        ("Relations", "State"),
        ("State", "Destination"),
    ),
)
```
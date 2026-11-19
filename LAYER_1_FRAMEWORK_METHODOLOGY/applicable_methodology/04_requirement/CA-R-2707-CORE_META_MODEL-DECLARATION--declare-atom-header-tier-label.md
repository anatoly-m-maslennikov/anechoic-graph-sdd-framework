---
atom_id: CA-R-2707
ref_id: CA-R-2707
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header.Context.Tier.Label
tier: 3
status: active
version: 5
updated_at: '2026-11-13T22:53:30.315950+00:00'
carrier_destination:
  file:
    name: CA-R-2707-CORE_META_MODEL-DECLARATION--declare-atom-header-tier-label.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2707-CORE_META_MODEL-DECLARATION--declare-atom-header-tier-label.md
  source_atom_id: CA-R-2707
  source_atom_revision: 5
  source_sha256: b6906cfebc2c139535a0d93dad37dd07666d96c365261077324655af3eff567b
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Atom.Header.Tier.Label

## Claim

### Prose Claim

When a Tier Label is present, Tier 1 requires Core, Tier 2 requires General, Tier 3 requires Standard, and Tier 4 requires Detail.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Label',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Context.Tier',
    value_format=str, value_cardinality=Cardinality(minimum=0, maximum=1), dependent_property_cardinality=0,
)
```


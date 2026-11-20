---
atom_id: CA-R-1634
ref_id: CA-R-1634
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Projection.Form
  dependencies:
  - ANECHOIC_MODEL <+ Projection
  - ANECHOIC_MODEL <+ Projection.Form
  - ANECHOIC_MODEL <+ Projection/(.Form:=Catalog)
  - 'ANECHOIC_MODEL <+ Projection/(.Form:=Map)'
  - 'ANECHOIC_MODEL <+ Projection/(.Form:=Hub)'
  - ANECHOIC_MODEL <+ Atom.Content
tier: 2
status: Active
version: 45
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-R-1634-CORE_META_MODEL-RULE--register-catalog-map-and-hub-as-type-values-under-projection.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Register Catalog, Map, and Hub as Type Values under Projection

## Claim

### Prose Claim


Projection Type values and derived terminology lists or vocabulary diagnostic indexes.


Catalog, Map, **and** Hub **must** be distinct Type values under Projection with no authority over linked Artifact Claims.

a derived terminology list **or** vocabulary diagnostic index **must** use Catalog as its Projection Type; its purpose **and** selected population do **not** admit another Type.

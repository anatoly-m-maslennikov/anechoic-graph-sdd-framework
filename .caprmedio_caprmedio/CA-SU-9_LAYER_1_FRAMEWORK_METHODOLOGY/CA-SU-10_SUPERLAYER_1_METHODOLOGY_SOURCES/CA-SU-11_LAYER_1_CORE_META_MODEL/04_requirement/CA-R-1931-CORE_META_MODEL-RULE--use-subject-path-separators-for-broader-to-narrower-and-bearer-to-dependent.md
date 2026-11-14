---
atom_id: CA-R-1931
ref_id: CA-R-1931
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics
  dependencies:
  - CAPRMEDIO_MODEL <+ Term//Property
  - CAPRMEDIO_MODEL <+ Entity/Property
  - CAPRMEDIO_MODEL <+ Relation//IS_PROPERTY_OF
  - CAPRMEDIO_MODEL <+ Relation//HAS_CLASSIFICATION
  - CAPRMEDIO_MODEL <+ Entity
  - CAPRMEDIO_MODEL <+ Entity/Object/Continuant/Package <+ Module <+ Code Unit
tier: 3
status: Active
version: 20
updated_at: '2026-11-11T18:31:44+04:00'
carrier_destination:
  file:
    name: CA-R-1931-CORE_META_MODEL-RULE--use-subject-path-separators-for-broader-to-narrower-and-bearer-to-dependent.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Use Subject Path Separators for Broader-to-Narrower and Bearer-to-Dependent

## Claim

### Prose Claim

- Use `X/Y` for a narrower declared kind, `X//Name` for a named instance, and `X.p` for a dependent Property.
- Use `X/(.p := V)` to select the qualified kind. Apply X’s inherited constraints to the selected kind. Existing Subjects using `:` retain their admitted interpretation.
- Keep the complete qualification of the Subject. The Subject expression can identify an existing target or one introduced by its defining Atom.
- Use the current Subject notation in CA-R-1321 for composition, classification, named Relations, and endpoint counts.

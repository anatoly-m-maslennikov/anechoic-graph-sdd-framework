---
atom_id: CA-M-121
ref_id: CA-M-121
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Continuant/Selection
tier: 3
status: active
version: 29
updated_at: '2026-11-13T18:59:42.538710+00:00'
carrier_destination:
  file:
    name: CA-M-121-CORE_META_MODEL-IMPLEMENTATION_METHOD--evaluate-scope-expressions.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-121-CORE_META_MODEL-IMPLEMENTATION_METHOD--evaluate-scope-expressions.md
  source_atom_id: CA-M-121
  source_atom_revision: 29
  source_sha256: b90baef9af77064c9b398020a5a1a2d82c6ecebd7d5a7b9cff071c9946cd8449
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary
Evaluate Scope Expressions

## Claim

### Prose Claim

evaluation of a historical CCE Scope Expression. This Method applies only to historical CCE material; it does not govern new Atom prose.

**to** evaluate one Scope Expression, the Resolver **must** perform **all** of:

1. resolve **every** exact Atom ID **or** other atomic identity **to** **`=1`** Governed Entity.
2. interpret **all** `<ENTITY_KIND>` as **every** Governed Entity of that kind within Atom Scope.
3. interpret **or** as set union.
4. interpret **and** as set intersection.
5. interpret **without** as left-side set exclusion.
6. interpret **where** as retention of **only** members whose field predicate evaluates **to** true according **to** `CA-M-122-CORE_META_MODEL-IMPLEMENTATION_METHOD--evaluate-condition-expressions`.
7. evaluate the innermost parenthesized set function **before** its containing set function.
8. use another Scope function **only** **when** an active CCE Method gives that function **`=1`** set meaning.

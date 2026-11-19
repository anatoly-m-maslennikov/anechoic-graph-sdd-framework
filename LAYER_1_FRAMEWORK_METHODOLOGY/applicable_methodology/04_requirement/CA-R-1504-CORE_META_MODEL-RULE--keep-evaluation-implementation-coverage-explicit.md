---
atom_id: CA-R-1504
ref_id: CA-R-1504
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Coverage
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Evaluation)
  - ANECHOIC_MODEL <+ Package/Project Package
  - ANECHOIC_MODEL <+ Atom.Content
tier: 1
status: Active
version: 26
updated_at: 2026-11-10 14:38:45 +0400
carrier_destination:
  file:
    name: CA-R-1504-CORE_META_MODEL-RULE--keep-evaluation-implementation-coverage-explicit.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1504-CORE_META_MODEL-RULE--keep-evaluation-implementation-coverage-explicit.md
  source_atom_id: CA-R-1504
  source_atom_revision: 26
  source_sha256: a6935b6e3f0ff6a23e26415e5ba754e4c83a383bccd8c262f132685bbd0dde99
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Keep Evaluation implementation coverage explicit

## Claim

### Prose Claim


coverage between Evaluation Atoms and their implementation realizations.


coverage between Evaluation Atoms **and** their realizations **may** be many-to-many **only** with explicit attribution:

- **`=1`** Evaluation Atom **may** be realized by multiple distinct implementations.
- **`=1`** implementation **may** realize multiple Evaluation Atoms **only** **when** its result remains attributable **to** **every** covered Claim.

## Details

a shared implementation **must not** make its covered Claims **or** their result attribution implicit. this Claim governs coverage, **not** a new Carrier **or** a second implementation registry.

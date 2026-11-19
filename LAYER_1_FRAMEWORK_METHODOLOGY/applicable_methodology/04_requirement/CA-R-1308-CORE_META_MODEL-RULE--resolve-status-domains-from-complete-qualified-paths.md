---
atom_id: CA-R-1308
ref_id: CA-R-1308
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom.Header.State.Status
  dependencies:
  - ANECHOIC_MODEL <+ Atom.Header.Context.Role
  - ANECHOIC_MODEL <+ Entity
tier: 1
status: Active
version: 27
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1308-CORE_META_MODEL-RULE--resolve-status-domains-from-complete-qualified-paths.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1308-CORE_META_MODEL-RULE--resolve-status-domains-from-complete-qualified-paths.md
  source_atom_id: CA-R-1308
  source_atom_revision: 27
  source_sha256: 1030fcc514e47c3fe82cb189560fda772d30881148ec23e6e27dd144dedcbff4
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Resolve Status Domains from Complete Qualified Paths

## Claim

### Prose Claim


Status domains resolved from complete qualified paths.


a global Status value domain **must not** override the Status domain resolved from the complete qualified path of an Artifact Type **or** Atom Content Role **and** Type.

## Details

for Atoms, resolution from the complete qualified Content Role and Type path includes the allowed values inherited from Atom.Header.Status and the additional values admitted for that path. Inheritance does **not** replace the qualified model with a flat global domain or remove its additions. A narrower Atom kind **must not** remove inherited Status values.

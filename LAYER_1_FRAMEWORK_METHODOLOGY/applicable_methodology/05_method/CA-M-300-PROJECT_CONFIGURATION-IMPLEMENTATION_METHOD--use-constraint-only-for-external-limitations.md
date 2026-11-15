---
atom_id: CA-M-300
ref_id: CA-M-300
container:
  scope_unit: CA-SU-13
role: Method
form: Implementation Method
topics:
  main_subject: 'CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form := Constraint)'
  dependencies:
  - 'CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement).Header.Context.Form'
  - CAPRMEDIO_MODEL <+ Project
  - CAPRMEDIO_MODEL <+ Actor
tier: 3
relations:
  method_for:
  - CA-R-1673@37
status: Active
version: 18
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-M-300-PROJECT_CONFIGURATION-IMPLEMENTATION_METHOD--use-constraint-only-for-external-limitations.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/05_method
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/05_method/CA-M-300-PROJECT_CONFIGURATION-IMPLEMENTATION_METHOD--use-constraint-only-for-external-limitations.md
  source_atom_id: CA-M-300
  source_atom_revision: 18
  source_sha256: ca4c341045e57778a0961987f702dc695858ee202ac1df1019a99b36b817b5bc
  original_relations_sha256: 2c1c0858a21e550a5bc21389ae2921541c58a9fe96c2481c42537051156a5e2f
---
## Summary
Use Constraint only for external limitations

## Claim

### Prose Claim

selection of a Requirement Type.


**to** select a Requirement Type, the Author **must** use Constraint **only** for a limitation imposed from outside the Project choice boundary.

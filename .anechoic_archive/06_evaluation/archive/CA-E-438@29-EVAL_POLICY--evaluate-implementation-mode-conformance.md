---
atom_id: CA-E-438
ref_id: CA-E-438@29
container:
  scope_unit: CA-SU-00
role: Evaluation
form: Eval Policy
topics:
  main_subject: ANECHOIC_MODEL <+ Package/Implementation
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Plan)
  - ANECHOIC_MODEL <+ Package/Implementation
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Requirement)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Method)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Delivery)
  - ANECHOIC_MODEL <+ Project
tier: 3
relations:
  child_of:
  - CA-E-001
  evaluation_for:
  - CA-M-266
  - CA-M-262
status: archived
version: 29
updated_at: 2026-11-02 08:06:47 +0400
carrier_destination:
  file:
    name: CA-E-438@29-EVAL_POLICY--evaluate-implementation-mode-conformance.md
    path: .anechoic_anechoic/06_evaluation/archive
cce_version: cce_1
cce_form: evaluation
llm_session_ids:
- codex:01a02650-eff7-7453-8c37-0699b36773c6
current_scope_unit: anechoic
---
## Summary
Evaluate implementation mode conformance

## Claim

### Prose Claim


the implementation mode Evaluation **must** return `fail` **if**

- execution replaces the Operator-selected mode **without** authorization,
- treats an evaluation-and-fix request as permission for a full rebuild,
- exceeds Task permissions,
- **or** exempts the selected mode from the governing RMED.

authorized rewriting **or** different source-code bytes **must not** by themselves cause failure **when** reconstruction equivalence under CA-M-262 is preserved.

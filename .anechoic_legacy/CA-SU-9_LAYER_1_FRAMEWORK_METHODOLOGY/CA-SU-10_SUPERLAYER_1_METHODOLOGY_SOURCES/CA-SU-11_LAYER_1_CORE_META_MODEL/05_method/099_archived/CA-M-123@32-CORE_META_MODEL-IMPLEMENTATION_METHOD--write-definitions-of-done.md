---
atom_id: CA-M-123
ref_id: CA-M-123@32
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  dependencies:
  - ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring
tier: 6
relations:
  child_of:
  - CA-M-1021
  - CA-M-122
  - CA-R-1581@23
  - CA-R-1583@26
status: archived
version: 32
updated_at: '2026-11-13T18:16:12.899091+00:00'
carrier_destination:
  file:
    name: CA-M-123@32-CORE_META_MODEL-IMPLEMENTATION_METHOD--write-definitions-of-done.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/099_archived
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Write Definitions of Done

## Claim

### Prose Claim


authoring one Definition of Done.


**to** write one Definition of Done, the Author **must** perform **all** of:

1. begin the falsification condition expression with: the Plan is **not** Done **if**.
2. make **every** atomic condition observable **and** decidable.
3. enclose **every** composite condition **and** **every** function argument **in** explicit parentheses.
4. evaluate the condition expression according **to** CA-M-122-CORE_META_MODEL-IMPLEMENTATION_METHOD--evaluate-condition-expressions.

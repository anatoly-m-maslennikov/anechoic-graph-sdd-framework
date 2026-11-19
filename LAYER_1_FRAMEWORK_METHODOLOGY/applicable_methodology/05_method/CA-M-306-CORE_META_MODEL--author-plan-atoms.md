---
atom_id: CA-M-306
ref_id: CA-M-306
container:
  scope_unit: CA-SU-11
role: Method
form: Implementation Method
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  - ANECHOIC_MODEL <+ Atom.Content
  - ANECHOIC_MODEL <+ Atom.Content.Summary
  - ANECHOIC_MODEL <+ Atom.Header.Context.Topics.Main Subject
  - ANECHOIC_MODEL <+ Relation//IS_BLOCKED_BY
  - ANECHOIC_MODEL <+ Relation//IS_CONTAINED_BY
  - ANECHOIC_MODEL <+ Scope Unit
  - ANECHOIC_MODEL <+ Carrier/File
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role:=Plan).Header.Context.Topics.Main
    Subject
tier: 2
status: Active
version: 36
updated_at: 2026-11-08 19:06:46 +0400
carrier_destination:
  file:
    name: CA-M-306-CORE_META_MODEL--author-plan-atoms.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/CA-M-306-CORE_META_MODEL--author-plan-atoms.md
  source_atom_id: CA-M-306
  source_atom_revision: 36
  source_sha256: 661de41830d8c1098aebb0b531c5e8a1a03d9263d8685a79310517f2dbd659d1
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Author Plan Atoms

## Claim

### Prose Claim

To author a Work Report, bind its Task through IS_WORK_REPORT_FOR, copy that Task’s Summary and Container, and record actual changes, checks, results and remaining gaps in Details. Update the record throughout execution.

For other Plan Forms, apply the common Plan rules independently of Label:

1. State the intended work or outcome and provide own work, direct Plan decomposition, or both under CA-R-1575. Apply the executable leaf-work bound under CA-R-1589.
2. Resolve the active Subject and its target Scope under CA-R-1588. Apply the applicable completion and verification rules, including CA-R-1599, and use Labels only under their governing rules. For a containing Plan whose Status is Done or Canceled, require every directly contained Plan to be Done or Canceled; mixed terminal statuses are allowed, and containment does not force a child Status to match the parent.
3. Express required start dependencies as direct `IS_BLOCKED_BY` Relations on the dependent Plan and derive `BLOCKS`. For Plan containment, declare `IS_CONTAINED_BY` on the child and derive `CONTAINS`. Do not infer dependencies from numbers or folder placement.
4. Resolve confidence from its applicable sources and store only an explicitly selected confidence override under its admitted encoding.
5. Review the finalized intended contribution against its supporting content and completion criteria, then derive Summary under CA-R-1418 and CA-R-2499. Preserve Summary across Revisions; a changed Summary requires the applicable replacement identity under CA-R-1464.

---
atom_id: CA-R-1559
ref_id: CA-R-1559
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Atom
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Header.Context.Plan.AI Agent Confidence Threshold
tier: 2
relations:
  child_of:
  - CA-M-261
status: Active
version: 28
updated_at: 2026-11-05 13:55:01 +0400
carrier_destination:
  file:
    name: CA-R-1559-RULE--gate-governing-atom-changes-during-implementation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1559-CORE_META_MODEL-RULE--gate-governing-atom-changes-during-implementation.md
  source_atom_id: CA-R-1559
  source_atom_revision: 28
  source_sha256: c9d03b47883cf0e160dd5428b569e465685f558bf53cf7bc7579fdbba66baba3
  original_relations_sha256: 94899af1df3add3533bb824b693365050895abf0a071adfe4339109a042cf4cb
---
## Summary

Gate governing Atom changes during implementation

## Claim

### Prose Claim

Changes to governing RMED Atoms during implementation.

Before a governing RMED Atom changes, resolve the effective Plan AI Agent Confidence Threshold under CA-R-2711, applicable permissions and additional Operator constraints. When confidence is below the threshold or an additional rule requires approval, request Operator disposition before changing the Atom. Autonomous change is allowed only when confidence meets the threshold and all applicable permissions and Operator constraints allow it. A prohibition remains a prohibition; confidence does not create permission.

An authorized RMED change establishes a new baseline under CA-M-262; resolve the affected work and Evaluations again against that baseline.

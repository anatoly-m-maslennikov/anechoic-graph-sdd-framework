---
atom_id: CA-R-1585
ref_id: CA-R-1585
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan).Assignee'
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Plan)
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/AI Agent
tier: 2
status: Active
version: 23
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1585-CORE_META_MODEL-RULE--default-plan-work-assignment-to-an-ai-agent.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1585-CORE_META_MODEL-RULE--default-plan-work-assignment-to-an-ai-agent.md
  source_atom_id: CA-R-1585
  source_atom_revision: 23
  source_sha256: 0eec43e73510b9f4288fb454267e7daa657fd300c765a707d9c874363f6bac32
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Default Plan work assignment to an AI Agent

## Claim

### Prose Claim


a Plan Atom with its own work and no explicit Assignee.


**if** a Plan Atom has its own work **and** no explicit Assignee, **then** its effective Assignee **must** be **=1** AI Agent selected **to** execute that work.

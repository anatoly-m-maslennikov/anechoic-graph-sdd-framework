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
---
## Summary

Default Plan work assignment to an AI Agent

## Claim

### Prose Claim


a Plan Atom with its own work and no explicit Assignee.


**if** a Plan Atom has its own work **and** no explicit Assignee, **then** its effective Assignee **must** be **=1** AI Agent selected **to** execute that work.

---
atom_id: CA-R-3006
ref_id: CA-R-3006
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Form := Scope Delegation)
tier: 3
status: active
version: 15
updated_at: '2026-11-14T13:56:40.432945+00:00'
carrier_destination:
  file:
    name: CA-R-3006-CORE_META_MODEL-DECLARATION--declare-scope-delegation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---
## Summary

Declare Scope Delegation

## Claim

### Prose Claim

Scope Delegation is one generic Form for an external Atom whose Role is in RMEDO. Its Main Subject identifies exactly one receiving non-Project Scope Unit within the Project. Its Container is that unit’s one direct structural Parent. Project may contain delegations for its children but is never their receiver. The direct Parent authors the structural declaration and assigns a contribution to the receiving unit; it retains its broader scope and accountability.

The Scope Unit Declaration states the structural facts for FORMAL_MODEL_GENERATOR.

During the Python migration, each Scope Unit listed below may have one separate Scope Unit Declaration alongside its existing Scope Delegation. The Declaration states the unit's Name, stable ID, ordering state, order number when ordered, direct containing Scope Unit, and structural level. Label remains optional. The existing Delegation retains its responsibilities and Main Subject boundaries. While both Claims state a structural fact, their values agree.

- AGENTIC (CA-SU-22)
- APPS (CA-SU-20)
- CODEX_EXTENSION (CA-SU-48)
- CODEX_HOOK (CA-SU-49)
- CONNECTOR_TOOLS (CA-SU-17)
- CORE_META_MODEL (CA-SU-11)
- FRAMEWORK_DELIVERY (CA-SU-27)
- FRAMEWORK_ENGINE (CA-SU-14)
- FRAMEWORK_METHODOLOGY (CA-SU-9)
- MCP (CA-SU-21)
- PROGRAMMATIC (CA-SU-15)
- PROJECT_TOOLS (CA-SU-19)
- PROMPTS (CA-SU-24)
- SKILLS (CA-SU-23)
- TOOLS (CA-SU-16)
- TOOL_WORKFLOWS (CA-SU-18)
- WORKBENCH (CA-SU-43)
- WORKBENCH_BACKEND (CA-SU-45)
- WORKBENCH_FRONTEND (CA-SU-46)

For each other Scope Unit that uses a combined Scope Delegation, that Delegation remains its structural declaration and states the same structural facts except structural level.

A Scope Delegation states the receiving Scope Unit's responsibilities and Main Subject boundaries in its Prose Claim. The applicable Model determines valid Role and Form combinations.

For local admission, the Atom's Container resolves to the receiving Scope Unit. Its Main Subject resolves to an endpoint admitted by at least one applicable Scope Delegation. A Plan / Work Report has the reported Task's Container and meets the applicable Main Subject boundaries.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Form', relation_name='IS_PROPERTY_OF',
    base_path='Atom.Header.Context', allowed_values=('Scope Delegation',),
    form_roles=('Requirement', 'Method', 'Evaluation', 'Delivery', 'Operations'),
)
```

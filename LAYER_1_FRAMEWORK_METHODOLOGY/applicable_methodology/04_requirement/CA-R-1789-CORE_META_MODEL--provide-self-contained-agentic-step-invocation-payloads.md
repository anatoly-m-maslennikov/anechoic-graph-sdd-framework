---
atom_id: CA-R-1789
ref_id: CA-R-1789
container:
  scope_unit: CA-SU-11
role: Requirement
form: Rule
topics:
  main_subject: ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run.Invocation Context
  dependencies:
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Workflow Run
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Workflow) >{1+} Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action)'
  - 'ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Action).Execution Kind'
  - ANECHOIC_MODEL <+ Entity/Object/Occurrent/Execution/Step Run.Agentic Step Execution Context
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Entity/Object/Continuant/Actor/Operator
  - ANECHOIC_MODEL <+ Journal
tier: 2
status: Active
version: 21
updated_at: 2026-11-02 00:18:22 +0400
carrier_destination:
  file:
    name: CA-R-1789-CORE_META_MODEL-RULE--provide-self-contained-agentic-step-invocation-payloads.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1789-CORE_META_MODEL--provide-self-contained-agentic-step-invocation-payloads.md
  source_atom_id: CA-R-1789
  source_atom_revision: 21
  source_sha256: 6a10decc6ede6d3bdc9fb894713105f0a248caf80a21b0ce9836261ece20c40d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Provide self-contained Agentic Step Invocation payloads

## Claim

### Prose Claim


an executor dispatching **or** resuming an Agentic Step.


the executor **must** provide a self-contained Invocation sufficient for the receiving context **to** perform the admitted Action **without** remembering the Workflow procedure from earlier conversation.

- identify the Workflow Run **and** Step Run, exact admitted definition bindings, bound inputs **or** accessible references, relevant prior results **and** actual effects, applicable permissions, **and** required output.
- provide the instruction derived from the Action **and** its Step binding, including how **to** return the result **or** request missing input. the instruction is a derived presentation of governing authority, **not** another independently maintained procedure.
- an Integrated Invocation returns this context **and** instruction through the session interface; an Isolated Invocation supplies it **to** the separate context. no particular transport is required by this core rule.

---
identity:
  atom_id: CA-M-1023
  ref_id: CA-M-1023
context:
  role: method
  form: Implementation Method
  tier: 4
  topics:
    main_subject: ANECHOIC_MODEL <+ Atom
    dependencies:
    - ANECHOIC_MODEL <+ Atom.Header.Context.Role
    - ANECHOIC_MODEL <+ Atom.Content
  container:
    scope_unit: CA-SU-11
state:
  version: 3
  status: active
  updated_at: '2026-11-13T19:02:14.892272+00:00'
destination:
  file:
    name: CA-M-1023-CORE_META_MODEL-IMPLEMENTATION_METHOD--apply-role-and-form-semantics-when-authoring-atoms.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method
---
## Summary

Apply Role and Form semantics when authoring Atoms

## Claim

### Prose Claim

Assess the declared Role and admitted Form against the primary contribution. Classify by meaning, not modality alone. Distinguish subordinate context from independently governed contributions. If classification or applicable authority is unresolved, identify the missing authority and do not claim conformance.

For intended Plan work, identify its action, object, intended result, effective Assignee, and applicable boundary. Keep supporting Details within that work or outcome; do not introduce a second intended outcome or Definition of Done. Reference separately governed requirements, reusable methods, and operational behavior. A Work Report follows its own Form.

For a Method, specify the applicable inputs, choices, dependencies, result, and unresolved choices needed to apply its design, mechanism, working approach, or local decision. Include performer, order, repetition, and stopping conditions when applicable.

For an Evaluation, state the expected observable evidence, acceptance policy, and condition and disposition for each applicable result as needed to reproduce the check. Make unavailable, unresolved, or contradictory required evidence explicit under the governed outcome; do not silently convert it to pass or fail. Separately reusable construction or selection belongs to Method, and reusable test-running behavior belongs to Operations.

For Delivery, identify the governed Entity or Carrier and its relevant representation, packaging, storage, placement, and availability constraints. State format, content, address, and lifecycle when relevant; use admitted typed Relations for representation bindings. Reference Requirement definitions of Entity, property, and Carrier kind. Do not invent fields or separate binding records merely to fill a template.

For an Operations Action, specify its applicable inputs, preconditions, behavior, results, observable effects, and failures. A leaf Step binds one Action or Workflow; a containing Step has Substeps and no own launch. Reference the called behavior without copying it. A Solution, Scope Delegation, Direct Policy, Approach Policy, or Decision does not itself create an executable binding merely by having Operations Role.

When validating, identify each mismatch by source occurrence, Role, Form, and controlling authority. Report unresolved required classification or evidence. Do not silently rewrite the source or claim conformance. Subordinate material from another Role is not automatically a second primary contribution.

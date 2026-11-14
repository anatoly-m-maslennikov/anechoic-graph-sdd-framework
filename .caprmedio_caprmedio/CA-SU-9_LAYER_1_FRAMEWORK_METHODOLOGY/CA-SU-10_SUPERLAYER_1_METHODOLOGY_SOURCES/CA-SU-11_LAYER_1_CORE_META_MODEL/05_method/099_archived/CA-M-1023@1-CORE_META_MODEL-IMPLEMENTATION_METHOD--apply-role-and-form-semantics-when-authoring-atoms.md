---
identity:
  atom_id: CA-M-1023
  ref_id: CA-M-1023@1
context:
  role: method
  form: Implementation Method
  tier: 4
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom
    dependencies:
    - CAPRMEDIO_MODEL <+ Atom.Header.Context.Role
    - CAPRMEDIO_MODEL <+ Atom.Content
  container:
    scope_unit: CA-SU-11
state:
  version: 1
  status: archived
  updated_at: '2026-11-13T18:15:09.857084+00:00'
destination:
  file:
    name: CA-M-1023@1-CORE_META_MODEL-IMPLEMENTATION_METHOD--apply-role-and-form-semantics-when-authoring-atoms.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/05_method/099_archived
---
## Summary

Apply Role and Form semantics when authoring Atoms

## Claim

### Prose Claim

Assess the declared Role and admitted Form against the Atom's primary contribution. Distinguish subordinate context from independently governed contributions. Classify the contribution by its meaning, not modality alone. If classification or applicable authority is unresolved, identify the missing authority and do not claim conformance.

For intended Plan work, identify the action, object, intended result, effective Assignee, and applicable boundary. Keep supporting Details within the intended work or outcome; do not introduce a second intended outcome or Definition of Done. Reference separately governed requirements, reusable methods, and operational behavior rather than making them the Plan's primary contribution. A Work Report records actual work and follows its own Form.

For a Method, specify the design, mechanism, working approach, or local decision with the applicable inputs, choices, dependencies, result, and unresolved choices needed to apply it. Include performer, order, repetition, and stopping conditions when applicable. Keep independently governed requirements, evaluation, delivery, and operational behavior in their own authority.

For an Evaluation, specify the evaluated subject, checked behavior, recoverable inputs or fixture, expected observable evidence, acceptance policy, and condition and disposition for each applicable result as needed to reproduce the check. Make unavailable, unresolved, or contradictory required evidence explicit under the governed outcome. Do not silently convert it to pass or fail. A checking procedure is part of the check; separately reusable construction or selection belongs to Method, and reusable test-running behavior belongs to Operations.

For Delivery, identify the governed Entity or Carrier and state relevant representation, packaging, storage, placement, and availability constraints. Include format, content, address, or lifecycle only when relevant. Use admitted typed Relations for representation bindings and reference Requirement definitions of Entity, property, and Carrier kind. Do not invent fields or separate binding records merely to fill a template.

For Operations, define an Action's single modeled operational responsibility and its applicable inputs, preconditions, behavior, results, observable effects, and failures. Define a Workflow graph through Step references, entry, declared order, routing, and terminal outcomes. A leaf Step binds one selected Action or Workflow; a containing Step has Substeps and no own launch. Put applicable parameter and input bindings at the Step, and reference reusable behavior rather than copying it. A Solution, Scope Delegation, Direct Policy, Approach Policy, or Decision does not itself create an executable binding merely by having Operations Role.

When validating, identify each mismatch by source occurrence, Role, Form, and controlling authority. Report unresolved required classification or evidence. Do not silently rewrite the source or claim conformance. Subordinate material from another Role is not automatically a second primary contribution.

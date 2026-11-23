---
atom_family: SPEC
atom_id: AN-S-2509
container:
  component: C9
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: '2026-11-13T18:15:09.857084+00:00'
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

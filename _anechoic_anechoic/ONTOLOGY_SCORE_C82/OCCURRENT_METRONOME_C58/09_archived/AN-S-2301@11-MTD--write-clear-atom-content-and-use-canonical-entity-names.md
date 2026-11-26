---
atom_family: SPEC
atom_id: AN-S-2301
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 11
  updated_at: "2026-11-25T22:48:37.041216+00:00"
---
## Summary

Write clear Atom content and use canonical entity names

## Claim

### Prose Claim

Write each Claim so its intended human reader can understand it and resolve exactly one precise interpretation. Name each necessary participant and relation. State each necessary modality, quantity, condition, and boundary. Do not use ambiguous pronouns, anaphora, ellipsis, unstated defaults, or mixed logical groupings. Make the meaning, conditions, and consequences clear.

In authored content, use each entity's exact admitted canonical name and use each governed Term with its authoritative meaning. Resolve the entity and its name before you mention it. Do not infer identity from spelling or substitute a synonym for an admitted name. When you describe a Carrier encoding, show the exact technical key as it appears in that format. If a required entity or Term binding is missing, ambiguous, or conflicting, report the uncertainty without inventing a name or meaning.

Apply the Atom's declared Template to its own contribution. A Spec can declare a requirement, design, check, or Carrier representation. Check its primary contribution and supporting sections under that Template even when it governs a Ticket, procedure, or Realization. Describe a Concern by the question, conflict, or problem to which it applies. Report each mismatch with the affected content, Template, and governing authority. Report missing or conflicting evidence explicitly. For a prose or reference finding, record the exact occurrence, observed and expected forms, and the authority revision. Cover exact names and references in sentence and list starts and in relevant Python, SQL, and Relation tokens. Record a Concern for unresolved evidence and preserve the source.

For a declarative Spec, name the governed entity or required result and state its observable boundaries. Put formal constraints in its Formal Manifest when expressible in the eDSL. Use prose for the remaining constraints. Use Semantics to explain the entity’s meaning. Put operative steps in the applicable procedure.

State applicability conditions and exclusions in the Content section defined by the Template. Keep one authoritative expression of a condition. For legacy RMED, keep formal conditions in the Formal Claim and textual conditions with the Prose Claim.

Split an Atom when part of its Claim can be accepted, replaced, or retired independently. Keep supporting details with the contribution they explain. If they change the contribution or its applicability, revise the affected source section explicitly.

For a procedure, identify its purpose, applicable inputs, choices, dependencies, output, and any unresolved decision. Give the performer, order, repetition, and stopping conditions where they affect execution. Reference independently governed constraints and checks.

For a Carrier rule, name the represented entity and state the applicable format, content, address, placement, storage, availability, and lifecycle. Use the declared Relation for a representation binding.

For a planning Ticket, state the intended action, object, result, and boundary. Record its assignee when known. A Ticket satisfied entirely through decomposition states the outcome and identifies its children. Keep Details within that outcome and write the Definition of Done under AN-S-2306.

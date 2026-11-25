---
atom_family: TKT
atom_id: AN-T-3904
container:
  component: C9
priority: 2
context:
  template: task
  label: Epic
state:
  status: backlog
  version: 1
  updated_at: '2026-11-24T11:45:00+00:00'
relations:
  IS_REFERENCE:
  - AN-C-3193@4-draft
  - AN-S-3108@3-draft
  - AN-S-3109@4-draft
  - AN-S-3111@3-draft
  - AN-S-3114@3-draft
  - AN-S-3115@5-draft
  - AN-S-3196@2-draft
  - AN-S-3312@2-draft
  - AN-S-4808@1-draft
  - AN-S-3118
  - AN-T-3476
---

## Summary

Meta-ontology refactoring

## Objective

Refactor the authoritative ANECHOIC Model in C9 and the Project Custom Model into Formal Manifests. Cover types, properties and axes, templates, relations, defaults, cardinality, and validation. Exclude generated and bundled copies as sources.

## Work

Update the authoring specification first. Define three typed, single-block Python forms: `manifest_node`, `manifest_property`, and `manifest_relation`. Use classes and types without repeated declaration wrappers. Resolve the existing authoring policy against the referenced Drafts.

Define node identity, including Atom `header.atom_id`. Keep dependent properties in their own carriers. Declare allowed outbound relations and cardinality. Derive inbound relations from authored edges.

Distinguish `value(default=...)`, an overrideable fallback, from `value(fixed=...)`, an invariant. For the Axiom, fix `container_type` to `Project` and require exactly one Project target.

Update the compiler and validator after the authoring specification. Pilot the Axiom before migration. Inventory the remaining declarations by owner and migrate only approved changes. Reuse the sibling Epic's whole-model verification.

## Acceptance

The authoring specification defines the three forms and their rules. The Axiom pilot demonstrates the fixed values and single Project target. Compiler and validator checks support the admitted forms.

The inventory covers the authoritative Model. Migration preserves existing semantics except approved changes. Whole-model validation checks parity and resolves missing or duplicate references.

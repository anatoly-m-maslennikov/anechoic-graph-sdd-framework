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
  status: "in_queue"
  version: 1
  updated_at: "2026-11-25T14:22:18.518815+00:00"

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

Start with a bundled reviewed Model that contains no Project-specific Manifests. Use it to ingest the Project, then query one fresh snapshot of active C9 and Project Config Formal Manifests. The existing Model service stages compilation and validation.

Publish a valid candidate as the Project’s last good Model. On failure, emit stderr and diagnostics and retain the last good Model, or the bundle on first boot.

Expose two accepted Model projections: the Primary tree and the bearer Property tree. Report the latest candidate Manifest findings for broken or undeclared paths, unresolved or duplicate references, constraints, and compatibility. Include attempt and accepted generation context.

Represent Project Structure as `mrt_project_structure`, with one row per Component. A watcher detects adds, edits, moves, and removals. Publish table rows atomically through existing ingestion. Do not hot-reload a Structure object or persist duplicate JSON.

An isolated managed Worker-to-Kernel run matched the approved Graph and Carrier candidate in SQL: 80 entities, 61 properties, and nine classification assignments. A malformed Axiom produced stderr and an SQL diagnostic while retaining the accepted fingerprint.

The candidate included the typed Carrier AN-S-1999@20. This was staged evidence; the selected carriers are now Active.

Complete the remaining review and adoption before release.

The selected carriers were published together in one coordinated source change.

Define named Lens groups in Project Manifest data. Expand each Component Manifest’s allowed scopes. Reject partial overlap during Structure validation.

## Acceptance

The authoring specification defines the three forms and their rules. The Axiom pilot demonstrates the fixed values and single Project target. Compiler and validator checks support the admitted forms.

The inventory covers the authoritative Model. Migration preserves existing semantics except approved changes. Whole-model validation checks parity and resolves missing or duplicate references.

A valid snapshot publishes both accepted projections. A failed candidate reports its findings and retains the correct fallback. Structure changes publish one coherent table generation.

Accept disjoint and nested scopes in one Component, including SWE with SWD. Reject SYS with BACKEND in one Component. Accept them in separate Components.

## Verification

The typed eDSL and authoritative Manifest migration passed compiler and Model checks. The Ontology Score hierarchy passed live Structure and release staging checks. The three original child Tasks are Done.

## Continuant Pitchfork follow-up

Review former E and QA for retirement. Review former M for retirement or a move to Occurrent Metronome.

Review former D only for filenames, paths, and admission of Markdown files and folders. Put each rule in the Manifest of the entity it governs, such as Atom or Component. Keep the Ontology engine-agnostic.

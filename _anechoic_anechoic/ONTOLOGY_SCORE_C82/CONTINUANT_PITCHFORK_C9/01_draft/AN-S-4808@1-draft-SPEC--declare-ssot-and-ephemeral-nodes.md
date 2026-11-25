---
atom_family: SPEC
atom_id: AN-S-4808
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-24T14:05:42+00:00'
---

## Summary

Declare SSOT and ephemeral Nodes

## Semantics

This Draft describes a proposed Graph Model. Graph contains Node, Relation, Classification, and eDSL. The eDSL contains Classes, including Format and Cardinality, and Functions. Graph entities and their relationships are distinct from the Files and Folders that carry them.

Artifact and Ephemeral are classifications. SSOT and Derived are Artifact classifications. SSOT captures prescribed, recorded, or realized information; Derived includes Projections. Ephemeral includes Session Context, Session Task, and Operative Plan.

Continuant and Occurrent are a separate temporal classification. Specification, Project Config, and Event Record are continuants; Ticket is an occurrent. Event Record is the recorded Artifact, distinct from the event it records.

The prescribed Model has Atom content and structure. Atom Family, Component, and Atom Companion Container describe structure. An Atom may logically own child Atoms, including Ticket children, and Assets. Its companion container supplies physical structure; moving containment there does not transfer logical ownership to the container.

Atom.Content and its descendant declarations remain authoritative. This Draft does not replace or remove it. The previous parity rehearsal did not include that DES declaration. Adoption must include it and its descendants in the source inventory and parity checks.

The Realization Model has Package structure and Module, Unit, Prompt, and Asset content. An Implementation Package includes Component Packages; a Test Package is a distinct Package. A Package may contain Packages, Modules, Prompts, and Assets; a Module may contain Units. Derived includes Projection.

A Project has exactly one Project Spec Component and exactly one Project Realization Package. The Component parent tree is shared by Specification and Component Package views. The Project Spec Component is the existing Project root for current Project validation and Axiom targeting; it is not a second Project identity. Keep the existing Project target and bindings until an explicit migration changes them.

### Atom Family names

Specification, Ticket, and Project Config are display names. Their Header wire values remain `SPEC`, `TKT`, and `PROJECT_CONFIG`, respectively. The ID markers remain `S`, `T`, and `C`; the legacy `P` marker remains recognized as Project Config under existing rules. Display names do not change stored Headers or IDs.

### Realization and binding

The referenced Spec Binding rule remains authoritative. The sidecar pins exact Atom revisions. `implements` derives `IMPLEMENTS` from the Realization Package to the pinned Spec and `IS_IMPLEMENTED_BY` in reverse. `applies` retains its distinct applied-Standard meaning and descendant coverage. Neither implies the other.

`TESTS` and `IS_TESTED_BY` remain separate, derived from the direct Test Package child as the referenced rule specifies, with or without a Spec Binding. A proposed `HAS_REALIZATION` view may reverse an existing `IMPLEMENTS` edge for its pinned Spec revision; it adds no independent binding and does not collapse `applies` or `TESTS` into implementation. Module-level edges require a separately specified source and are not inferred from a Package binding.

### Adoption and evidence

This is a design Draft, not an executable Model declaration. Adoption requires a separate Model change and binding migration. Until admitted, current declarations, Project validation, source recognition, and relation derivation remain authoritative.

1. Inventory each proposed subject and relationship against Active scoped declarations, including Atom.Content and descendants. Record identity, scope, ownership, and all changed bindings.
2. Author one typed, scoped carrier per declared subject using the admitted claim form. Preserve existing subject identities where semantics are unchanged.
3. Prepare and validate the binding migration, including Project compatibility, logical ownership, exact revisions, applicability, implementation inverses, and separate test edges. Explicitly resolve any subject or relation the current compiler cannot express before cutover.
4. Exercise authoring admission and compile the candidate from those carriers. Compare the resulting Model and binding projections with the intended mappings and retained Active behavior, including Atom.Content. Record diagnostics and source inventory.
5. Admit and verify the generation through the runtime path before changing consumers or retiring legacy declarations. Evidence must identify the accepted generation and cover both authoring and runtime admission. Failed or missing evidence blocks adoption.

The scoped carriers, compiler support where needed, migration, and runtime admission are deferred to that adoption change. This design alone does not claim compiler or runtime acceptance.

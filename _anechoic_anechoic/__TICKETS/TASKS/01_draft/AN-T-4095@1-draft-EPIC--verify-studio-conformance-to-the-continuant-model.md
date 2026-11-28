---
atom_family: TKT
atom_id: AN-T-4095
container:
  component: C75
priority: 2
context:
  template: task
  label: Epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-28T09:23:35.351609+00:00'
---

## Summary

Verify Studio conformance to the Continuant Model

## Objective

Use the admitted Model from Ontology / Continuant as the authority
for types, properties, relations, and constraints in Studio code.
Start in Spec Engine. Add a child Component if its verification
responsibility warrants a separate boundary.

## Fixed rules

Studio can hardcode the current carrier shape and the primitives needed
to read it.

- The base Atom and the current set of Header properties, including
  nested properties such as `state.status` and `context.template`.
- The YAML Header, Markdown Content, and current carrier formats.
  Summary is the only fixed Content property. Read all other Content
  properties and their constraints from the admitted Model.
- The Status Groups Draft, Current, and Archived. Ready belongs to
  the Draft group. Keep the stored Status name `ready` until its
  rename. Read exact allowed Status values from the admitted Model.
- Ref ID formatting from Atom ID, Version, and the applicable carrier
  marker.
- Version allocation. Start a new Atom identity at 1. Allocate the
  next Version when the lifecycle operation creates a new revision.
- The generation and serialization of `state.updated_at` as a
  timestamp with a UTC offset. The lifecycle operation determines
  when to set it.
- The base Relation and the representation of its endpoints.
- The base Component and its identity fields `id`, `name`, and
  `parent`. Read their values from the Component Manifest carrier.

The admitted Model is the single source of truth for the exact allowed
values of Header properties. Studio reads the effective values at
runtime from the admitted Model or its generated declarations. The
Model also supplies Relation names and constraints, classification
axes, Atom Templates, families, and lifecycle rules.

Project Config supplies Project-specific Model declarations. Admit
them with the base Continuant Model and read the effective rules from
the admitted Model. For example, AN-C-3194 declares the Project's
Axiom Template and its Tier, Lens, and container type. The Axiom
Atoms themselves live under the Project.

The Project Manifest is the source of truth for Project settings.

Review any other fixed rule against what Studio needs before it can
load the Model or Project Manifest. Manifest discovery and source
format version checks are candidates for this review.

## Work

- Align SPEC and Ticket indexing with the revision namespaces in
  AN-S-4913 and AN-S-4914. Keep `ready` in the SPEC Draft namespace.
  Check carrier placement and existing Ref IDs when migrating the index.
- Keep Active predecessors when finalizing a SPEC as Ready. Archive
  the same-ID Active predecessor and Active targets of
  `IS_REPLACEMENT_FOR` at activation, as specified by AN-S-1846.
- Verify the formal uniqueness and containment invariants against
  Studio. Check Status-dependent Ref IDs and Updated At offsets
  against their Model semantics.
- Find Studio literals for Header value domains and Content properties
  other than Summary. Read them from the admitted Model. Read Project
  settings from the Project Manifest.
- Map Studio boundaries to the Model rules that apply to them.
  Import public Model types and validators where they can apply those
  rules directly. Reuse the admitted Model and its generated outputs.
- Compare Model-to-Lean with independently generated Code-to-Lean.
  Record the exact Model and code pins, the checked rules,
  contradictions, and unsupported cases.
- Add Static checks that run without Lean for rules visible in source
  and generated declarations. Check that generated outputs refer to
  the same admitted Model as the Studio code that uses them.
- Generate Unit and Functional tests from Model rules. Include valid
  and invalid examples. Run Functional tests through real Studio
  interfaces and verify that violations produce the expected errors.
- Pilot one Studio boundary. Confirm that the checks catch a Model
  violation and a stale Model fingerprint. Establish which checks
  belong in the existing QA gates.

## Acceptance

One Studio boundary uses the public Model where applicable.
Both Static paths and the generated tests run against the same
pinned Model. The violations and stale-Model controls fail as
expected. The report identifies rules that remain unchecked.

Change one Model rule and verify that Studio follows it after loading
the updated Model. The change requires no edits to Studio code.

## Stage 1 results

AN-T-4096 records the C53 pilot, generated cases, and Lean comparison.
AN-T-4097 and AN-T-4098 track the two findings outside Spec Engine.

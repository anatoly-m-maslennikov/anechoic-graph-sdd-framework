---
identity:
  atom_id: CA-R-3187
  ref_id: CA-R-3187@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:10.875678+00:00'
destination:
  file:
    name: CA-R-3187@1-draft-CORE_META_MODEL-REQUIREMENT--bind-spec-atoms-to-existing-realization-with-trace-sidecars.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Bind Spec Atoms to existing Realization with trace sidecars

## Claim

### Prose Claim

A sidecar records trace bindings between Spec Atoms and existing Realization, such as a Component Package, ordinary Package, boundary module, or Unit. It can record `implemented` and `applied` bindings; a version pin identifies an exact Atom revision. Resolve Realization paths from the selected Project root. Start with the link between a Component Spec Section and its Component Package; list Standards as applied at the Component Package, with their scope covering that Component’s Realization and descendant Components. Mapped passing QA checks provide evidence for the behavior they exercise. Sidecars are trace records; SPEC defines the Contracts.

## Details

Acceptance: a sidecar associates an existing module under the selected Project root with the exact revision of a Spec Atom; a path that does not resolve to existing Realization fails the binding check. A mapped passing test supports only the behavior it exercises.

Sources: CA-A-1463@1-draft, CA-A-1465@1-draft. Task: CA-P-3083.

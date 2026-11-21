---
atom_family: SPEC
atom_id: AN-S-3014
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-20T15:43:09.394572+00:00'
---
## Summary

Bind Spec Atoms to existing Realization with trace sidecars

## Claim

### Prose Claim

A sidecar records trace bindings between Spec Atoms and existing Realization, such as a Component Package, ordinary Package, boundary module, or Unit. It can record `implemented` and `applied` bindings; a version pin identifies an exact Atom revision. Resolve Realization paths from the selected Project root. Start with the link between a Component Spec Section and its Component Package; list Standards as applied at the Component Package, with their scope covering that Component’s Realization and descendant Components. Mapped passing QA checks provide evidence for the behavior they exercise. Sidecars are trace records; SPEC defines the Contracts.

The Package sidecar is the Spec Binding file. Store it at the Package root as
`<package folder name>__spec_bind.yaml`, using the full directory name. Use the
YAML keys `implements` and `applies` for the two binding types. Each key has a
list of exact Atom version pins. Omit a key when its list has no entries.

Each `implements` entry records `IMPLEMENTS` from the Realization Package
to the pinned Spec Atom. Read the inverse as `IS_IMPLEMENTED_BY`.

For a Realization Package, recognize its direct
`<full package folder name>__tests/` subdirectory as its Test Package.
Derive `TESTS` from the Test Package to its parent Realization Package.
Read the inverse as `IS_TESTED_BY`. This derivation does not require a Spec
or a Spec Binding for the parent Package.

## Details

Acceptance: a sidecar associates an existing module under the selected Project root with the exact revision of a Spec Atom; a path that does not resolve to existing Realization fails the binding check. A mapped passing test supports only the behavior it exercises.

A direct `create_order_pkg3344__tests/` directory supplies one `TESTS`
edge to `create_order_pkg3344`. A similarly named sibling or deeper
directory supplies no such edge.

Sources: CA-A-1463@1-draft, CA-A-1465@1-draft. Task: CA-P-3083.

---
atom_family: SPEC
atom_id: AN-S-3035
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:50.701000+00:00'
---
## Summary

Define Component lens whitelists

## Claim

### Prose Claim

A Lens is an optional named grouping of viewpoints. A lens name has one meaning across the Project: a Component can declare a new lens only under a name unused in the Project, and uses an existing lens by reference. Wherever enabled, a lens resolves to the same detailed lenses.

A Component's effective whitelist is the list declared by its own Manifest, if present; otherwise it is the nearest ancestor's declared list. The selected list replaces higher lists in full. An explicit empty list clears inheritance. If neither the Component nor any ancestor declares a list, no lenses are enabled. SPEC is available only when included in the effective list.

## Details

The mechanical migration writes each Component's `lens_whitelist` from
the lenses of its mapped Atoms. The Project Manifest includes `SPEC`
for itself and the Project Goal. Meta-ontology retains the temporary
whitelist in CA-A-1462.

Acceptance: with no declarations in a Component's ancestry, its effective list is empty; with parent `[SPEC, DES]` and no local list, it inherits that list; a child declaration `[SWE]` replaces it with `[SWE]`; an explicit child `[]` yields no enabled lenses. A second Component cannot redefine an existing lens name with different detailed lenses.

Sources: CA-A-1462@1-draft, CA-P-3081@1. Task: CA-P-3081.

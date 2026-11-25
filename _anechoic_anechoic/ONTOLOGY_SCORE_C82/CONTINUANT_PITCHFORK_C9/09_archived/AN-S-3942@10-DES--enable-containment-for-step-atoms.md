---
atom_family: SPEC
atom_id: AN-S-3942
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-27 20:00:07 +0400
---
## Summary

Enable containment for Step Atoms

# Summary

Enable containment for Step Atoms

## Scope

Containment capability of Step Atoms, including nested substeps.

## Claim

`Atom/Content Role: Operations/Type: Step.Enabled Relations.Contains` **must** be True. a Step Atom **may** contain other Step Atoms. a containing Step with substeps has no own Action launch.

## Details

A substep is a nested Step, not a separate Type. a leaf Step, including a leaf substep, launches **exactly one** referenced reusable Action with its parameters **and** input bindings; a containing Step owns its nested substeps and launches no Action of its own. Containment is optional and can nest. This permission does not change a Step's Action reference or input bindings, prescribe how internal tool calls are modeled, or introduce a storage layout or execution protocol.

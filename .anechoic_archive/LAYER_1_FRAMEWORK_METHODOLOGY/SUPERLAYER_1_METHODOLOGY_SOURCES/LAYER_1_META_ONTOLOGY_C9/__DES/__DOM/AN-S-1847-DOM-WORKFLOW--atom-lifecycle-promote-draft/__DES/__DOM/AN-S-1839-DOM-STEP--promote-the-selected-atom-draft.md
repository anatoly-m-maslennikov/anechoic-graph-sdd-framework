---
atom_family: SPEC
atom_id: AN-S-1839
container:
  atom: AN-S-1847
tier: 3
context:
  template: step
  lens: DES/DOM
state:
  status: active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
---
## Summary

Promote the selected Atom Draft

## Claim scope

One exact non-container Draft binding within [Atom Lifecycle_Promote Draft](../CA-O-10018-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-promote-draft.md).

## Claim

### Kind

Execution.

### Inputs

Selected Draft, allowed Current `targetStatus`, optional `savedArchivedAtom`, and `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Promote one Atom Draft](../CA-O-10005-PROJECT_CONFIGURATION-ACTION--promote-one-atom-draft.md).

### Outputs

The called Action's declared Outputs.

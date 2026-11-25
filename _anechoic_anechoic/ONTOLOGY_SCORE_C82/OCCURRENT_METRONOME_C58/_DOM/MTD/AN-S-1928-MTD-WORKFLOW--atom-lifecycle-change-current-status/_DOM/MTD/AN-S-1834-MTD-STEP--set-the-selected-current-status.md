---
atom_family: SPEC
atom_id: AN-S-1834
container:
  atom: AN-S-1928
tier: 3
context:
  template: step
  lens: DOM/MTD
state:
  status: active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
---
## Summary

Set the selected Current Status

## Claim scope

One Current-Status binding within [Atom Lifecycle_Change Current Status](../CA-O-10011-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-change-current-status.md).

## Claim

### Kind

Execution.

### Inputs

Selected Atom, requested `targetStatus`, and `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Set one Current Atom Status](../CA-O-10007-PROJECT_CONFIGURATION-ACTION--set-one-current-atom-status.md).

### Outputs

The called Action's declared Outputs.

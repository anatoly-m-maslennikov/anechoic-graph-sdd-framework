---
atom_family: SPEC
atom_id: AN-S-1844
container:
  atom: AN-S-1852
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

Promote the prepared Draft

## Claim scope

One bound prepared Draft within [Atom Lifecycle_Update Atom](../CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom.md).

## Claim

### Kind

Execution.

### Inputs

Bind `savedDraft`, captured `targetStatus`, `savedArchivedAtom`, and `projectContext` to the called Workflow. The called Workflow skips the target already archived by this Update.

### Fixed parameters

None.

### Runs

The Workflow [Atom Lifecycle_Promote Draft](../CA-O-10018-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-promote-draft.md).

### Outputs

The called Workflow's declared Output.

---
atom_family: SPEC
atom_id: AN-S-1843
structure:
  container:
    atom: AN-S-1852
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

Create the Draft for a new Version

## Claim scope

One bound Current-backed proposal within [Atom Lifecycle_Update Atom](../CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom.md).

## Claim

### Kind

Execution.

### Inputs

Bind `sourceCurrent`, requested changes, `projectContext` to the called Workflow. Keep `targetStatus` in the enclosing Workflow context.

### Fixed parameters

None.

### Runs

The Workflow [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md).

### Outputs

The called Workflow's declared Output.

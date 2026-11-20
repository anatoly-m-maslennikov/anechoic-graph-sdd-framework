---
atom_family: SPEC
atom_id: AN-S-1842
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

Archive the exact Current Version

## Claim scope

One bound exact Current source within [Atom Lifecycle_Update Atom](../CA-O-10024-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom.md).

## Claim

### Kind

Execution.

### Inputs

Bind the original `sourceCurrent`, `projectContext` to the called Workflow. `targetStatus` remains enclosing-Workflow context.

### Fixed parameters

None.

### Runs

The Workflow [Atom Lifecycle_Archive Atom](../CA-O-10009-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-archive-atom.md).

### Outputs

The called Workflow's declared Output.

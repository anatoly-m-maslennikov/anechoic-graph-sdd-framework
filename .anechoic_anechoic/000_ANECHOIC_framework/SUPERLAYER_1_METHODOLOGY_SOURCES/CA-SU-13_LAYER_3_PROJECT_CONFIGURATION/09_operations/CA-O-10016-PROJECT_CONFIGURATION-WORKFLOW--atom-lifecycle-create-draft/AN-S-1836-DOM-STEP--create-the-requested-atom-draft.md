---
atom_family: SPEC
atom_id: AN-S-1836
structure:
  container:
    atom: AN-S-1838
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

Create the requested Atom Draft

## Claim scope

One non-container Draft request passed by [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md).

## Claim

### Kind

Execution.

### Inputs

Validated `parameters`, warnings, `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Create one Atom Draft](../CA-O-10003-PROJECT_CONFIGURATION-ACTION--create-one-atom-draft.md).

### Outputs

The called Action's declared Outputs.

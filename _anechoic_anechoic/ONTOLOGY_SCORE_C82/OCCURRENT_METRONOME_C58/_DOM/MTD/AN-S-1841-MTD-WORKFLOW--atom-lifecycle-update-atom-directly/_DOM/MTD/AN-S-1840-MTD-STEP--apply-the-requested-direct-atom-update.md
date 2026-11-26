---
atom_family: SPEC
atom_id: AN-S-1840
container:
  atom: AN-S-1841
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

Apply the requested Direct Atom Update

## Claim scope

One bound non-container Atom within [Atom Lifecycle_Update Atom Directly](../CA-O-10023-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-update-atom-directly.md).

## Claim

### Kind

Execution.

### Inputs

Selected Atom; requested changes; `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Apply one Direct Atom Update](../CA-O-10000-PROJECT_CONFIGURATION-ACTION--apply-one-direct-atom-update.md).

### Outputs

The called Action's declared Outputs.

---
atom_family: SPEC
atom_id: AN-S-1835
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

Check Draft input

## Claim scope

One accumulated Draft request from [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md).

## Claim

### Kind

Decision.

### Inputs

Accumulated `parameters` and `projectContext`.

### Fixed parameters

None.

### Runs

The Action [Check Draft input formats and allowed values](../CA-O-10002-PROJECT_CONFIGURATION-ACTION--check-draft-input-formats-and-allowed-values.md).

### Outputs

`parameters`, `requested_input`, and warnings returned by the called Action.

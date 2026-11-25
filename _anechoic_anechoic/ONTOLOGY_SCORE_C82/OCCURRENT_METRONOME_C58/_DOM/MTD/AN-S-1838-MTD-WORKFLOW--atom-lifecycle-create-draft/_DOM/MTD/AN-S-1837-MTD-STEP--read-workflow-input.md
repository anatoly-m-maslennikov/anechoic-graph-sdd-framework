---
atom_family: SPEC
atom_id: AN-S-1837
container:
  atom: AN-S-1838
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

Read Workflow input

## Claim scope

One root or nested invocation of [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md) and its input dictionary.

## Claim

### Kind

Input.

### Inputs

The invocation dictionary declared by the called Action; `projectContext`; the bound Workflow Run and request.

### Fixed parameters

None.

### Runs

The Action [Read Workflow intake input](../CA-O-10006-PROJECT_CONFIGURATION-ACTION--read-workflow-intake-input.md).

### Outputs

Bind the returned invocation dictionary to `parameters`.

---
atom_family: SPEC
atom_id: AN-S-1851
container:
  atom: AN-S-1838
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
---
## Summary

Request Draft input

## Claim scope

One correction-input binding within [Atom Lifecycle_Create Draft](../CA-O-10016-PROJECT_CONFIGURATION-WORKFLOW--atom-lifecycle-create-draft.md).

## Claim

### Kind

Input.

### Inputs

Accumulated `parameters`, `requested_input`, intermediate results, warnings, `projectContext`, and the bound Workflow Run and current Step.

### Fixed parameters

None.

### Runs

The Action [Present intermediate results and request input](../CA-O-10004-PROJECT_CONFIGURATION-ACTION--present-intermediate-results-and-request-input.md).

### Outputs

The called Action's waiting response or resumed correction dictionary, with its results and warnings. Merge a resumed dictionary only into fields named in `requested_input`; preserve all other caller parameters. The captured `targetStatus` cannot be replaced by corrections.

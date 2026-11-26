---
atom_family: SPEC
atom_id: AN-S-1851
container:
  atom: AN-S-1838
tier: 3
context:
  template: step
  lens: DOM/MTD
state:
  status: active
  version: 2
  updated_at: 2026-11-11 17:36:30 +0400
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

The called Action's waiting response or resumed correction dictionary, with its results and warnings. Merge the supplied corrections into the retained caller parameters. A caller can supply only the requested fields and can also correct other caller inputs. Preserve fields the caller omits and retain the internally captured `targetStatus`. Validate the merged input before applying effects.

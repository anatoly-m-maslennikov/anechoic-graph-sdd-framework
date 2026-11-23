---
atom_family: SPEC
atom_id: AN-S-4717
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-23 01:47:30 +0400
---
## Summary

Read execution status and saved results

# Summary

Read execution status and saved results

## Scope

the GET_EXECUTION_STATUS capability for Tool/GET_EXECUTION_STATUS.

## Claim

the GET_EXECUTION_STATUS Tool **must** return the saved Workflow Run status and requested Action results with evidence references, distinguishing work outcomes from evidence-recording failures.

## Details

- implement the methodology Action CA-O-115-PROJECT_CONFIGURATION-ACTION--get-execution-status.
- accept a supported Run ID, optional Action ID and selection ordinal, and whether full saved results are requested; return status, output, results, progress, recording blockers, and report references.
- preserve the Operator's choice of what **to** execute; discovery, context retrieval, **and** observation provide capabilities.
- bounded **or** unavailable evidence **must** remain explicit **rather than** establish a successful assessment.

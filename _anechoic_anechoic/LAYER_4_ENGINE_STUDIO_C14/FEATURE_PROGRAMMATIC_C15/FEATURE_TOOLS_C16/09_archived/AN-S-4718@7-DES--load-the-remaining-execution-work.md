---
atom_family: SPEC
atom_id: AN-S-4718
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Load the remaining execution work

# Summary

Load the remaining execution work

## Scope

the RESUME_EXECUTION_CONTEXT capability for Tool/RESUME_EXECUTION_CONTEXT.

## Claim

the RESUME_EXECUTION_CONTEXT Tool **must** return sufficient saved context to continue unfinished work under the same Run ID without replaying completed effects.

## Details

- implement the methodology Action CA-O-116-PROJECT_CONFIGURATION-ACTION--load-the-remaining-execution-work.
- accept a supported Run ID; return original request, frozen selection and criteria bindings, pending check or fix work, saved handoffs, current-source observations, and recording blockers.
- preserve the Operator's choice of what **to** execute; discovery, context retrieval, **and** observation provide capabilities.
- bounded **or** unavailable evidence **must** remain explicit **rather than** establish a successful assessment.

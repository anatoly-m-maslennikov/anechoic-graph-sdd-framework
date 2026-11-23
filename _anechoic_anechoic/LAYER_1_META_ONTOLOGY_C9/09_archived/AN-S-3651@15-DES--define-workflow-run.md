---
atom_family: SPEC
atom_id: AN-S-3651
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Define Workflow Run

# Summary

Define Workflow Run

## Scope

the Workflow Run entity.

## Claim

a Workflow Run **means** **`=1`** actual execution of **`=1`** Workflow against the inputs **and** parameters supplied for that run.

## Details

- the execution follows the Workflow's typed Relations **and** retains its actual Step Runs, outcomes, **and** applicable retry allowance.
- the run is distinct from the reusable Workflow **and** from the Journal Records that describe its execution. a reference **to** the definition does **not** prove that a run occurred.

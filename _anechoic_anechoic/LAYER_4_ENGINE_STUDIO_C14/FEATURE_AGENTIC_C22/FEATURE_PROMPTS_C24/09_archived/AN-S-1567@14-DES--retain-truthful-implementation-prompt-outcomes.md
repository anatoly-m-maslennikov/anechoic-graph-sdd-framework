---
atom_family: SPEC
atom_id: AN-S-1567
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Retain truthful implementation prompt outcomes

## Claim scope

result and evidence returned by a current Implementation Workflow prompt.

## Claim

### Prose Claim

the Implementation **must** return only a result label admitted by its current Step plus actual outputs, input/source bindings, retained state, evidence references, and blockers; absent or unperformed checks never become a passing result.

## Details

An initial expected failing Evaluation consumes zero retries. Diagnosis, retry admission, repair, and renewed checking retain real state; a repair does not imply success. Method learning remains a separate CA-O-102 Workflow.

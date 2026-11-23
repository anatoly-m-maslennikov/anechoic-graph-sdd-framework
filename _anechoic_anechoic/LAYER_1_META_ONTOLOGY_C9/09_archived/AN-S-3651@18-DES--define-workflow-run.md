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
  version: 18
  updated_at: 2026-10-29 07:32:39 +0400
---
## Summary

Define Workflow Run

## Claim scope

the Workflow Run entity.

## Claim

A Workflow Run means one actual execution of exactly one Workflow against the inputs and parameters supplied for that run. The execution follows the Workflow's typed Relations and retains its actual Step Runs, outcomes and applicable retry allowance. A Workflow Run is distinct from the reusable Workflow and from the Journal Records that describe its execution; a reference to the definition does not prove that a run occurred.

### Formal claim

```text
Workflow Run ((IS_EXECUTION_OF)) Workflow
```

## Details

CA-A-1260 makes the existing one-Workflow binding formal. The run remains distinct from the definition and any Event Record about it.

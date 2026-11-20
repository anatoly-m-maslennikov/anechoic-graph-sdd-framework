---
atom_family: TKT
atom_id: AN-T-112
structure:
  container:
    component: C00
  priority: 2
context:
  template: Spec Proposal
state:
  status: done
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Limit Workflow calls to Steps

## Decision

The Operator selected Workflow calls only in Steps. A Substep calls exactly one Action with parameters; it cannot call a Workflow and cannot contain further Substeps. Step and Substep remain distinct kinds. The choice between Action and Workflow targets belongs only to a leaf Step. A containing Step runs its declared Substeps and makes no call of its own.

## State

Definition Draft preparation only. Current sources, Workflow instances and Engine implementation are unchanged.

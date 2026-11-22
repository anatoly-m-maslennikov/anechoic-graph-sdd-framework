---
atom_family: TKT
atom_id: AN-T-122
container:
  component: C00
priority: 2
context:
  template: Spec Proposal
state:
  status: complete
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Retain the settled Workflow container hierarchy

## Decision

The container hierarchy is already settled:

```text
Workflow >{>=1} Step >{>=0} Substep
```

A Workflow contains at least one Step. A Step may contain zero or more Substeps. Each Step belongs to exactly one immediate Workflow; each Substep belongs to exactly one immediate Step. Containment is not specialization.

Do not reopen this hierarchy as a separate choice between independent entities and embedded content, or introduce extra Operations Types on that basis. The established leaf-call boundaries and permission for recursive Workflow calls remain unchanged.

## State

The Workflow, Step and Substep Definition Drafts and Model proposal use the Operator's latest cardinality spelling. Current source adoption, catalog reconciliation and Engine implementation remain pending.

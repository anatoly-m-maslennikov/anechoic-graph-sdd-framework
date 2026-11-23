---
atom_family: TKT
atom_id: AN-T-120
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 21:51:04 +0400
---
## Summary

Allow recursive Workflow calls

# Summary

Allow recursive Workflow calls

## Decision

A Workflow may call itself directly, or indirectly through other Workflows. The Workflow-call graph is not required to be acyclic.

Calls remain subject to the accepted Step boundaries: only a leaf Step calls a Workflow, with parameters and input bindings. Substeps call Actions only; a Step containing Substeps makes no call of its own. Referencing a Workflow does not structurally contain or copy its definition.

This decision adds no mandatory recursion-depth limit, termination proof, retry budget or automatic guard. It permits recursive definitions without promising that every possible run terminates.

## State

Workflow and Step Definition Drafts and the Model proposal are updated. Current definitions, concrete Workflows and Engine/runtime behavior are unchanged.

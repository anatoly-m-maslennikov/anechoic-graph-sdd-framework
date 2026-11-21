---
atom_family: TKT
atom_id: AN-T-111
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

Allow Steps to call Workflows

## Decision

A leaf Step calls exactly one Action with parameters or exactly one Workflow with parameters. A Step containing Substeps makes neither kind of call itself. Calling a reusable Workflow is distinct from containing that Workflow definition; the caller contains its Steps, not the called Workflows. No wrapper Action or new invocation entity is introduced.

## Operator example

Update Atom Workflow:
1. Step: call Create Draft Workflow with parameters.
2. Step: call Archive Atom Workflow with parameters.
3. Step: call Promote Draft Workflow with parameters.

These names illustrate the call structure only. No new project-specific Workflow Atom is created by this example. Workflow call-cycle rules are not decided by this increment.

## State

Definition Draft preparation only. Current sources, Workflow instances and Engine implementation are unchanged.

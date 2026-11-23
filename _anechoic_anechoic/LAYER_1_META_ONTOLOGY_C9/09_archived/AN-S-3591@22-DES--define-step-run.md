---
atom_family: SPEC
atom_id: AN-S-3591
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 22
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Define Step Run

## Claim scope

Actual executions of Steps within Workflow Runs.

## Claim

A Step Run is one actual execution of one Step within one enclosing Workflow Run. Every executed Step, including a containing Step, has its own distinct Step Run.

A leaf Step Run follows its Step's bound call target. An Action call executes through the corresponding Action Run; a Workflow call executes through the corresponding called Workflow Run. A containing Step Run executes its declared Sub-steps and makes no Action or Workflow call of its own; each Sub-step invokes its bound Action.

Separate executions of a Step are distinct Step Runs. Definitions remain reusable and are not copied for each execution. A recorded attempt or failure must not be represented as successful completion.

## Semantics

The enclosing Workflow Run and a Workflow Run called by a leaf Step are different execution roles. Calling a Workflow does not require an artificial wrapper Action or Action Run. The Step Run remains distinct from its definition and from Event Records describing it.

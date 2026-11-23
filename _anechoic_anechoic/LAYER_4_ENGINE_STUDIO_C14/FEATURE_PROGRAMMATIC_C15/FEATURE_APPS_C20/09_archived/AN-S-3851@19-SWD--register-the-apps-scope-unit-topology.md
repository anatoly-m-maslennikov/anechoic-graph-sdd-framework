---
atom_family: SPEC
atom_id: AN-S-3851
container:
  component: C20
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:40 +0400
---
## Summary

Register the APPS Scope Unit topology

# Register the APPS Scope Unit topology

## Applicable when

Use this Method **when** registering **or** changing an immediate APPS Scope Unit.

## Procedure

1. Resolve the active APPS authority **and** the current immediate-child Scope Unit declarations.
2. Register `GRAPH_SERVER`, `GRAPH_UI`, `WORKFLOW_ORCHESTRATOR`, **and** `AGENT_HOST_PLUGINS` as distinct immediate unordered APPS children.
3. Assign the headless read model **and** service to `GRAPH_SERVER`; assign the optional human interface to `GRAPH_UI`; assign Workflow Run state **and** continuation to `WORKFLOW_ORCHESTRATOR`; **and** retain host-specific packaging in `AGENT_HOST_PLUGINS`.
4. Verify that `GRAPH_SERVER` exposes the complete headless boundary required by Tools **and** MCP without depending on `GRAPH_UI`.
5. State that every read model, interface, **and** Projection is derived support **and** does **not** become project authority.
6. Confirm that each declaration has one immediate typed owner, one identity, **and** no conflicting owner **or** responsibility claim.

## Outcome

APPS has four identifiable immediate unordered children with separated server, optional UI, orchestration, **and** host-plugin responsibilities.

## Failure or stop

Stop **when** a required child is missing, duplicated, non-immediate, ordered, assigned a conflicting boundary, **or** given project authority; also stop when headless behavior depends on `GRAPH_UI`.

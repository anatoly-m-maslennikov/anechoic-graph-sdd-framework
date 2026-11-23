---
atom_family: SPEC
atom_id: AN-S-3853
container:
  component: C20
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 7
  updated_at: 2026-09-23 04:20:00 +0400
---
## Summary

Verify the APPS Scope Unit topology

# Verify the APPS Scope Unit topology

## Claim checked

CA-M-196 registers the four immediate unordered APPS units with distinct responsibilities **and** without project authority.

## Applicable when

Apply whenever an immediate APPS child's ownership, structural identity, responsibility boundary, **or** realization path changes.

## Test case

Examine the current active APPS authority and its child declarations, using derived representations only as supporting evidence. Exercise graph access once with `GRAPH_UI` absent.

## Acceptance criteria

`GRAPH_SERVER`, `GRAPH_UI`, `WORKFLOW_ORCHESTRATOR`, **and** `AGENT_HOST_PLUGINS` are distinct immediate unordered APPS children. `GRAPH_SERVER` operates headlessly for Tools **and** MCP; `GRAPH_UI` remains optional; orchestration state belongs to `WORKFLOW_ORCHESTRATOR`; **and** no child becomes project authority.

## Failure disposition

Reject the topology and preserve the examined authority, supporting evidence, **and** every missing, duplicate, dependent, **or** conflicting boundary.

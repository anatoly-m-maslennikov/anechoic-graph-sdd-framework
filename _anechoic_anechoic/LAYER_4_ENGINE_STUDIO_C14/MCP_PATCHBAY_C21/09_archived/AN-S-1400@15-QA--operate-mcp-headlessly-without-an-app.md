---
atom_family: SPEC
atom_id: AN-S-1400
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Operate MCP headlessly without an App

# Operate MCP headlessly without an App

## Claim checked

the project-local provider-neutral MCP service exposes an eligible Tool **without** App **or** plugin presentation.

## Test case

Start the MCP service **without** `GRAPH_UI` **or** an agent-host plugin **and** invoke one eligible Tool, retrieve one ACTION_PROMPT invocation, **and** start one Workflow until its next interaction boundary.

## Acceptance criteria

the Tool remains discoverable **and** callable, the prompt returns its self-contained invocation envelope, **and** the Workflow returns its next resumable state through the one project-local service.

## Failure disposition

Reject an MCP deployment that depends on an App **or** transfers provider-neutral ownership **to** a plugin.

---
atom_family: SPEC
atom_id: AN-S-3581
container:
  component: C20
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 5
  updated_at: 2026-10-23 23:09:56 +0400
---
## Summary

Coordinate local Runs with DBOS

# Summary

Coordinate local Runs with DBOS

## Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

## Claim

implement independent execution through DBOS durable queues **and** a separately started local worker.

## Details

1. validate **and** freeze the submitted request before queue admission; duplicate Run IDs accept **only** the same frozen request.
2. register **=1** Project queue with concurrency **=1** initially, preventing competing source edits.
3. use durable Steps for gather, Agent dispatch, admitted report recording **and** finalization; workflow ordering is gather, check, fix, with no recheck.
4. expose queue state through a client adapter; keep DBOS checkpoints operational, with confirmed Workflow events **in** the shared Journal.
5. start the worker explicitly. installation **or** discovery starts no Run **and** installs no hook.

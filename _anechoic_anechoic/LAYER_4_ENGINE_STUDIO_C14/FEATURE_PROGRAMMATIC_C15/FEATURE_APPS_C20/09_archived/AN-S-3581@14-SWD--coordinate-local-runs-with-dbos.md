---
atom_family: SPEC
atom_id: AN-S-3581
container:
  component: C20
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 14
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Coordinate local Runs with DBOS

## Claim

### Prose Claim

implement independent execution through DBOS durable queues **and** a separately started local worker.

## Details

### Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

1. validate **and** freeze the submitted request before queue admission; duplicate Run IDs accept **only** the same frozen request.
2. register **=1** Project queue with concurrency **=1** initially, preventing competing source edits.
3. use durable Steps for gather, Agent dispatch, admitted report recording **and** finalization; workflow ordering is gather, check, fix, with no recheck.
4. expose queue state through a client adapter; keep DBOS checkpoints operational, with confirmed Workflow events **in** the shared Journal.
5. start the worker explicitly. installation **or** discovery starts no Run **and** installs no hook.

### Conditional future AI-Agent execution

Agent-result parsing, mock-Agent scheduling and Agent dispatch, where mentioned above, apply only to separately admitted AI-Agent execution. The retained deterministic contract does not start or restore an Agent runtime.

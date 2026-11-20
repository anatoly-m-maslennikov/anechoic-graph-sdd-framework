---
identity:
  atom_id: AN-S-2815
context:
  container:
    component: C34
  tier: 3
  lens: SWD
state:
  status: draft
  version: 1
  updated_at: 2026-10-23 18:22:28 +0400
---
# Summary

Execute queued Single Actions and record results

## Scope

The leaf execution boundary for queued SINGLE_ACTIONS work in the shared TOOLS
runtime.

## Claim

ACTION_ENGINE is a leaf execution unit and carries no locally owned policy;
it may inherit applicable governing policy. It consumes
queued work, invokes Single Actions through ADAPTERS, and stores outcomes for
the schedulers. The shared queue and run state are the runtime boundary: the
engine accepts a queued run and returns a `RunID`, so callers need not remain
connected.

## Details

MCP is a thin interface to this runtime, not separate orchestration logic.
Runtime-state persistence is not Journal history, and this Method invents no
automatic recovery mechanism. Do not deploy a separate service per Scope Unit.

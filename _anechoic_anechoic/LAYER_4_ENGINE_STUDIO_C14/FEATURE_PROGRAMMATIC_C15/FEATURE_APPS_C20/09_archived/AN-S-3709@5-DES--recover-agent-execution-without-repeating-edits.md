---
atom_family: SPEC
atom_id: AN-S-3709
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Recover Agent execution without repeating edits

# Summary

Recover Agent execution without repeating edits

## Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

## Claim

WORKFLOW_ORCHESTRATOR **must** recover interrupted execution **without** replaying a completed Atom edit.

## Details

- use a stable dispatch identity for each selected Atom **and** phase.
- retain accepted Agent output before source effects. admit reports through the existing coordination Tool.
- before applying an accepted edit, compare the current source with the saved before **and** after hashes: apply the before case, acknowledge the after case, **and** block any other case.
- a worker loss **during** unacknowledged Agent execution leaves execution uncertain; require explicit recovery rather than silently launching another effectful session.
- transport retry does **not** grant semantic repair permission. replay recorded completed outputs rather than rerunning completed checks.

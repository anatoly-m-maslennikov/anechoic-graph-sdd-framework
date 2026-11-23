---
atom_family: TKT
atom_id: AN-T-815
container:
  component: C14
priority: 2
context:
  template: task
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 08:10:13 +0400
---
## Summary

Define the Engine implementation Workflow

# Summary

Define the Engine implementation Workflow

## Objective

Define one FRAMEWORK_ENGINE implementation Workflow whose Steps consume the selected RMED authority through the new Tools.

## Details

Author the project-local O Workflow, Steps and Actions, and the supporting RMED in their owning Engine units. Reuse useful current implementation contracts and replace conflicting stale bindings; do not create a second implementation procedure. Define inputs, each Step's output, permitted effects, failure reporting and Operator-controlled start. Each runtime Step runs in a fresh subagent; the coordinator passes saved outputs rather than relying on session memory.

Execute this Task in its own subagent. Preserve unrelated work; the integration owner controls shared files and Git. Split only genuinely oversized own-work into smaller P Tasks before execution. This Task grants no live operation outside the selected implementation scope.

## Definition of Done

The current O flow and supporting RMED describe the requested test-first sequence, one fresh subagent per Step and the new Tool boundaries; source review finds no legacy direct-write fallback.


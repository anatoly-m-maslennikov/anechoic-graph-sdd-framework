---
atom_family: SPEC
atom_id: AN-S-4603
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Admit an implementation repair retry

# Summary

Admit an implementation repair retry

## Operation

Implementation Retry Control Step **means** the Workflow node invoking **=1** Action, CA-O-024, **in** Integrated context under CA-R-1527.

- bind inputs from the diagnosed failures from CA-O-234, effective retry sources, retained consumed count, selected P/Plan, current governing permissions, **and** effective confidence threshold.
- use the host's native session/subagent, file, **and** command capabilities; this binding has no MCP prerequisite. missing required context **or** capability returns a blocked invocation, **not** silent execution **in** another context.
- retain exact Action/Step Revisions, source bindings, actual effects, **and** returned results. pass the Action's result **to** the Workflow **without** independently copying its behavior.

map the Action's admitted-retry decision **to** `retry_permitted` **and** **every** exhausted, prohibited, unresolved, **or** approval-blocked decision **to** `retry_blocked`. preserve CA-O-024 accounting **without** another retry counter.

## Details

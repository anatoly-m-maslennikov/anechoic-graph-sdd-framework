---
atom_family: SPEC
atom_id: AN-S-4652
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: '2026-10-21T23:57:54+00:00'
---
## Summary

Diagnose failures in the assigned subagent

# Summary

Diagnose failures in the assigned subagent

## Operation

Implementation Failure Diagnosis Step **means** the Workflow node invoking **=1** Action, CA-O-089, **in** Isolated context under CA-R-1527.

- bind inputs from the same assigned implementation subagent context, selected P/Plan, current candidate **and** phase, failure evidence from CA-O-094, test definitions, current Method Projection **and** R/E/D, **and** applicable confidence **and** permission gates.
- use the host's native session/subagent, file, **and** command capabilities; this binding has no MCP prerequisite. missing required context **or** capability returns a blocked invocation, **not** silent execution **in** another context.
- retain exact Action/Step Revisions, source bindings, actual effects, **and** returned results. pass the Action's result **to** the Workflow **without** independently copying its behavior.

reuse the assigned subagent for the selected P work across its test, implementation, diagnosis, **and** repair invocations **when** available. replacement requires the complete retained input/evidence handoff **and** fresh admission; do **not** rely on unrecorded conversational memory.

## Details

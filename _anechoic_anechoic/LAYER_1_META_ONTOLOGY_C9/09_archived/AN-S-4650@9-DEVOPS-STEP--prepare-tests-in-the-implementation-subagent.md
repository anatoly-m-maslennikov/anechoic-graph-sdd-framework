---
atom_family: SPEC
atom_id: AN-S-4650
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

Prepare tests in the implementation subagent

# Summary

Prepare tests in the implementation subagent

## Operation

Evaluation Implementation Step **means** the Workflow node invoking **=1** Action, CA-O-018, **in** Isolated context under CA-R-1527.

- bind inputs from the selected P/Plan item, assigned subagent context, governing Method Projection, R/E/D, owned work boundary, current candidate **and** tests, **and** admitted prerequisites returned by CA-O-091.
- use the host's native session/subagent, file, **and** command capabilities; this binding has no MCP prerequisite. missing required context **or** capability returns a blocked invocation, **not** silent execution **in** another context.
- retain exact Action/Step Revisions, source bindings, actual effects, **and** returned results. pass the Action's result **to** the Workflow **without** independently copying its behavior.

reuse the assigned subagent for the selected P work across its test, implementation, diagnosis, **and** repair invocations **when** available. replacement requires the complete retained input/evidence handoff **and** fresh admission; do **not** rely on unrecorded conversational memory.

## Details

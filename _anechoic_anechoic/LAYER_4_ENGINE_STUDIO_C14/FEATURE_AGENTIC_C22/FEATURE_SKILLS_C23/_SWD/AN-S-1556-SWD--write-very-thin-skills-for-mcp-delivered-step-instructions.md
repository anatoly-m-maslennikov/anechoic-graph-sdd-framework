---
atom_family: SPEC
atom_id: AN-S-1556
container:
  component: C23
tier: 4
context:
  lens: SWD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T10:14:10.362056+00:00"
---
## Summary
Write very thin Skills for MCP-delivered Step instructions

## Claim

### Prose Claim

**to** author a very thin Skill under the thin-Skill boundary, separate stable bootstrap **and** response-handling instructions from the task-specific instructions supplied by the framework.

- Use a short discovery description that identifies the Skill purpose.
- keep the standing body limited **to** framework connection, the admitted request/result interface, **and** generic response, failure, missing-input, **and** escalation handling. explain how **to** consume the current invocation **without** embedding the decisions performed by its Action.
- Use the host-configured ANECHOIC MCP with the explicit Project root.
- Read the selected MCP tool help as required. Load any additional context for the task on demand.
- Follow the applicable approval and delegation rules.

the result is a bounded Skill wrapper that remains valid **when** task-specific Action instructions change **without** changing the wrapper interface. **if** authoring reveals a missing interface, source, **or** authority binding, report that gap rather than hide it inside the Skill. this Method governs authoring; it does **not** define a new session Workflow **or** promote another Draft.

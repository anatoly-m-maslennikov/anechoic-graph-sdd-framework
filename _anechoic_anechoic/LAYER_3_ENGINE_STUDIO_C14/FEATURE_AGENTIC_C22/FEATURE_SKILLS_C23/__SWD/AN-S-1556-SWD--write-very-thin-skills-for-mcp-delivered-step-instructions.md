---
atom_family: SPEC
atom_id: AN-S-1556
container:
  component: C23
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary
Write very thin Skills for MCP-delivered Step instructions

## Claim

### Prose Claim

**to** author a very thin Skill under the thin-Skill boundary, separate stable bootstrap **and** response-handling instructions from the task-specific instructions supplied by the framework.

- use a short discovery description that identifies the entry purpose **and** its registered route **when** applicable; do **not** put a Workflow procedure **in** the description.
- keep the standing body limited **to** framework connection, the admitted request/result interface, **and** generic response, failure, missing-input, **and** escalation handling. explain how **to** consume the current invocation **without** embedding the decisions performed by its Action.
- reference the portable shared runtime and canonical PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ APIs, **not** scripts maintained inside the Skill.
- let the current MCP response supply the Action prompt **and** its Step bindings. retain accessible references for additional current-Step context rather than preloading the MODEL//ANECHOIC <+ Atom/(.Header.Role in RMED) **or** unrelated prompts.
- follow the existing delegation **and** Step-context rules. do **not** author another approval policy, routing tree, continuation table, **or** delegation procedure inside the Skill.

the result is a bounded Skill wrapper that remains valid **when** task-specific Action instructions change **without** changing the wrapper interface. **if** authoring reveals a missing interface, source, **or** authority binding, report that gap rather than hide it inside the Skill. this Method governs authoring; it does **not** define a new session Workflow **or** promote another Draft.

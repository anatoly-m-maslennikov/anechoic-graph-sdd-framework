---
atom_family: SPEC
atom_id: AN-S-2325
structure:
  container:
    component: C15
  tier: 5
context:
  lens: SWD
state:
  status: active
  version: 20
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---

## Summary

Record business Workflow lifecycle separately from technical diagnostics

## Claim



### Prose Claim
Keep technical diagnosis on structured stdout/stderr streams and record actual business Workflow lifecycle events through the declared Journal owner, without turning a technical warning into a business event.

## Details

### Scope

New or changed PROGRAMMATIC implementation, including Tools, Apps, MCP adapters and their public operation boundaries.

1. Emit technical diagnostics through the shared logger with the actual Project prefix and sanitized context. The Docker runtime captures these streams under its bounded retention/back-pressure configuration; use stderr when stdout carries MCP/Tool protocol or result data.
   For the Project Atom Lifecycle backend, emit a stdout INFO event when each step starts and when it ends as done or failed. Include the step and elapsed time in the end event. Keep input values and carrier contents out of the log.
2. Apply CA-M-396 to severity: input and Project artifact issues use WARNING; ERROR is reserved for real blocking runtime failures. Do not confuse a response error or a failed business Workflow with ERROR-level logging.
3. For an actually admitted/started business Workflow, record its observed started, failed and completed lifecycle transitions, as applicable, through its executor and the shared Journal owner. A technical cause may explain a real business failure without copying technical log records or stack traces into the Journal.
4. A preflight rejection with no admitted/started business Workflow must not fabricate a Workflow, Run, started/failed event or completion event. Direct read-only Tool calls do not gain hidden Journal effects from logging or generic error handling.
5. Keep business records truthful and independent from Git and technical-log retention. Journal incompleteness is not an admission gate. Preserve existing historical Journal bytes and do not rewrite old technical entries as part of this Method.

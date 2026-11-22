---
atom_family: TKT
atom_id: AN-T-2972
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T00:19:17.142169+00:00"
---
## Summary

Review recent MCP errors and add regression coverage

## Work

This is the first behavioral testing task for AN-T-2944, as authorized by the Operator. Review retained ANECHOIC MCP error evidence from 2026-11-20 00:05:06 UTC through 2026-11-22 00:05:06 UTC.

Separate product defects from expected refusals, client input errors, and environment failures. Reproduce each verified bug through its public interface. Add end-to-end coverage for cross-Component behavior or a short canary check for startup or readiness regressions.

Use disposable runtime state and record evidence coverage gaps. Verify each regression against the affected behavior. Other Epic work stays on hold.
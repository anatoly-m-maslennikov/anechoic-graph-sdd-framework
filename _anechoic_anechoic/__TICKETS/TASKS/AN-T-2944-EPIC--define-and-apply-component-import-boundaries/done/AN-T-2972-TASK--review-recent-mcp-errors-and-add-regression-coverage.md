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
  status: done
  version: 2
  updated_at: "2026-11-22T00:22:06.011068+00:00"
---
## Summary

Review recent MCP errors and add regression coverage

## Work

This is the first behavioral testing task for AN-T-2944, as authorized by the Operator. Review retained ANECHOIC MCP error evidence from 2026-11-20 00:05:06 UTC through 2026-11-22 00:05:06 UTC.

Separate product defects from expected refusals, client input errors, and environment failures. Reproduce each verified bug through its public interface. Add end-to-end coverage for cross-Component behavior or a short canary check for startup or readiness regressions.

Use disposable runtime state and record evidence coverage gaps. Verify each regression against the affected behavior. The Operator subsequently authorized the full Epic through the Goal.

## Findings

- Docker retained logs from 2026-11-21 23:46:46 UTC onward. They showed 19
  instances of one MCP notification delivery failure while a session was
  closing. The logs did not identify the initiating request or prove that
  health checks caused the incidents.
- Workbench retained 498 successful and 17 failed SQL calls in the review
  window. Sixteen failures were syntax or binding errors. The remaining
  query referenced `specs`, a table absent from the exposed schema.
- Retained project Codex responses included generic runtime failures,
  transport outages, and rejected input. Those records did not establish a
  second reproducible product defect.

## Completion evidence

The image health check now waits for MCP ping before closing the session.
The release canary executes one read-only query after MCP initialization
and checks its result. For Projects that disable that query explicitly, it
checks MCP ping.

The Docker end-to-end test verifies successful queries in two successive
sessions with normal closure. It verifies session continuity. The retained
SDK failure's initiating request remains unknown.

Eight focused checks passed. The new Docker test and the release canary
passed on the same disposable image,
`sha256:64d5f9e4c57de41d96017d18c747f368921585a9c7abb598d837732eb56e8ec0`.

---
atom_family: TKT
atom_id: AN-T-2009
container:
  component: C45
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Invalid SQL and arguments are logged as blocking runtime failures.

## Concern

Invalid SQL and invalid query arguments were logged as blocking `ERROR` even
when the Workbench runtime remained healthy. This conflated a failed request
with a failed runtime and obscured whether the owner could continue serving
requests.

## Resolution

`query_error` now uses `WARNING` with outcome `failed`; an actual Workbench
runtime failure remains `ERROR` with outcome `blocked`. The focused
`test_runtime_failure_diagnostics.py` checks pass 9 tests, MCP HTTP checks pass
13, and a native SDK flow succeeds after the failed request. This resolves the
source diagnostic classification; deployment adoption remains separate.

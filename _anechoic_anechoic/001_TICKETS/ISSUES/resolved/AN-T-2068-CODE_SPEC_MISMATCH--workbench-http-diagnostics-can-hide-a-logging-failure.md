---
atom_family: TKT
atom_id: AN-T-2068
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-20T20:35:37.550635+00:00'
---
## Summary

Workbench HTTP diagnostics can hide a logging failure

## Claim

### Prose Claim

CA-M-396@17 requires both the primary failure and a secondary diagnostics failure to remain observable. `FEATURE_MCP/workbench_web.py` calls `report_failure` but drops its secondary failure while building the HTTP response. The client sees the primary failure with no indication that its diagnostic could not be recorded.

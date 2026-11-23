---
atom_family: TKT
atom_id: AN-T-1536
container:
  component: C00
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:34 +0400
---
## Summary

Repair sealed MCP startup and query fixtures

# Summary

Repair sealed MCP startup and query fixtures

## Objective

repair the MCP fixtures to use the declared sealed source context and retain bounded startup diagnostics.

## Details

test_rmed_workflow_mcp.py; demonstrate protocol, gather/check/fix and registered query discovery in a source-equivalent sealed fixture.

## Definition of Done

the confirmed defect is explained and repaired against current authority; source-equivalent focused regressions have a captured terminal result and independent review accepts the bounded change. actual full Release acceptance remains with the parent Plan.

## Acceptance evidence

independent review accepts canonical selected-manifest/query-source fixture construction and bounded startup stderr. after final frozen D580 v7/D572 v16 publication, the designated host-tests interpreter completed all four MCP fixture tests in 12.935 seconds, exit 0. no legacy live-tree authority fallback or weakened query coverage was introduced.

this is bounded fixture acceptance only; actual complete Release acceptance remains with CA-P-1809 and CA-P-1117.

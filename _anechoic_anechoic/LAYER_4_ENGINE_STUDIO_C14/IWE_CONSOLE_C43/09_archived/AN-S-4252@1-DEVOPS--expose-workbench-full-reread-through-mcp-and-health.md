---
atom_family: SPEC
atom_id: AN-S-4252
container:
  component: C43
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 13:52:40 +0400
---

## Summary

Expose Workbench full reread through MCP and health

## Claim scope

The selected Project's Workbench service operation in the existing MCP gateway and health page.

## Claim

Expose the native MCP service tool `workbench_reread({})` and a health-page Full reread action through the same Workbench gateway operation. The operation has no generic service name, shell command, container argument or service registry. Add `workbench_reread` to the `Service` group of the generated `discover_tools` catalog. MCP and health use the same Project selection, operation and explicit failure boundary. The health page remains available when Workbench is unavailable. The operation does not restart MCP, another service or the container, and does not write a business Journal event.

## Details

The health action is an explicit POST to `/anechoic/health/workbench-reread`; GET remains read-only. In shared mode it carries the existing explicit `project_root` form field; the single-Project action accepts no body. It reports success only after the full reread is ready and reports the same failure when source validation or startup fails.

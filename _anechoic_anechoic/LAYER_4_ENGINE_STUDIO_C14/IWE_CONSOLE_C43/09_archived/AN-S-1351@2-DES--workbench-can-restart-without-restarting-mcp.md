---
atom_family: SPEC
atom_id: AN-S-1351
container:
  component: C43
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-05 06:00:43 +0400
---

## Summary

Workbench can restart without restarting MCP

## Claim

Allow the Operator or an AI Agent to restart the selected Project's Workbench through MCP or a health-page button without restarting MCP, other services or the container. Restart closes the old Workbench owner, rebuilds its index from the admitted Current/Draft Atom sources and Current Scope Unit Declarations, and clears temporary query results. It preserves source files and saved queries and Worksheets. Return success only after the replacement Workbench is ready. If sources or startup remain invalid, return an explicit failure and leave Workbench unavailable until another explicit restart. Do not retry automatically.

## Details

An invalid Scope Unit Declaration continues to stop indexing and require explicit restart. Fixing its file alone does not restart Workbench. The service operation is synchronous and does not create a Workflow, queue, background restart job or Business Journal event.

Opening the health page does not restart anything. Restart requires an explicit button action, and its result is visible on that page. The health button and MCP expose the same operation and preserve the same data.

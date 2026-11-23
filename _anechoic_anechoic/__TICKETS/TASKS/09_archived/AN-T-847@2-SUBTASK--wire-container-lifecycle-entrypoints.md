---
atom_family: TKT
atom_id: AN-T-847
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 2
  updated_at: 2026-10-24 06:04:41 +0400
---
## Summary

Wire container lifecycle entrypoints

# Summary

Wire container lifecycle entrypoints

## Objective

Connect the sealed container preview and technical coordinator to actual MCP/worker/status entrypoints.

## Details

At most 15 minutes own work; split before extending. Root owns existing selected_routes.py, selected_native_providers.py and backend.py plus focused integration tests. Depend on P2500 pure seal and P2499 caller interface. Preserve one-Atom lifecycle_admission unchanged; add separate observed.container_lifecycle only to root MCP preview. Worker verifies original full seal then ordinary per-member admissions. Status must identify technical coordinator separately from actual member Runs and never invent a terminal root Workflow Run. No production MCP port, dependency, release, deployment or migration.

### Definition of Done

Focused synthetic-project checks and independent review verify the stated behavior without live MCP tests, deployment, migration, or held-batch replay. Review dependent next Task before acceptance execution.

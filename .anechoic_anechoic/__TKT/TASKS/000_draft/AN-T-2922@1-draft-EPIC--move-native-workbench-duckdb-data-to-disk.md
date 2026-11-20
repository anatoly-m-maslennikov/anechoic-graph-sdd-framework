---
identity:
  atom_id: AN-T-2922
context:
  container:
    component: C43
  tier: 3
  template: epic
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T12:51:11.462381+00:00'
---
## Summary

Move native Workbench DuckDB data to disk

## Objective

Store the native Workbench projection, parsed imports, and temporary query result tables in a Project-local DuckDB file. Let the Operator rebuild any table or all tables on demand.

## Work

1. Add a Tier 1 Decision in Workbench Backend (C45) for disk-backed storage and ownership.
2. Update [AN-S-2536](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/SWD/AN-S-2536-SWD--reconcile-duckdb-derived-state-from-a-stable-governed-inventory.md) to specify startup validation and explicit rebuilds of one table or all tables, including dependent tables and DuckPGQ registration.
3. Update [AN-S-3086](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/SWD/AN-S-3086-SWD--publish-and-query-the-import-graph-through-workbench.md) to specify disk-backed raw import records, cache validation, and reconciliation of source changes made while Workbench was stopped.
4. Add a Spec for disk-backed temporary query result tables that covers paging, pinning, expiry, restart behavior, and rebuild from retained SQL.
5. Update [AN-S-1366](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/QA/AN-S-1366-QA--query-native-sql-results-and-typed-relation-expansion.md) with acceptance checks for restart reuse, result cleanup, and on-demand rebuilds.

## Definition of Done

The Tier 1 Decision and supporting Spec Atoms are reviewed against the existing Spec and code.

## References

[AN-T-2915](../done/AN-T-2915-EPIC--deliver-the-module-and-package-import-graph.md)

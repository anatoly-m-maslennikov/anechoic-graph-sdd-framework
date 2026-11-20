---
identity:
  atom_id: AN-T-2922
context:
  container:
    component: C43
  tier: 3
  template: epic
state:
  status: "draft"
  version: 1
  updated_at: "2026-11-20T15:54:00.809800+00:00"
---
## Summary

Move native Workbench DuckDB data to disk

## Objective

Store the native Workbench projection, parsed imports, and temporary query result tables in a Project-local DuckDB file. Let the Operator rebuild any table or all tables on demand.
Extend the Import Graph into the Realization Graph. Reuse its Module and
Package nodes for folder-derived test Relations.

## Work

### Stage 1. Prepare the Spec

Prerequisite. Admit the native `REFERENCES` Relation and its Header target forms before moving Stage 1 citations into Atom Relations.

1. Create the [Tier 1 Solution Decision AN-S-3116](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-3116@1-draft-DES-DECISION--store-native-workbench-duckdb-data-on-disk.md).
2. Update [AN-S-1362](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/000_draft/AN-S-1362@19-draft-DEVOPS--place-the-duckdb-projection-in-rebuildable-runtime-state.md) for runtime storage and startup.
3. Update [AN-S-2536](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-2536@32-draft-SWD--reconcile-duckdb-derived-state-from-a-stable-governed-inventory.md) for reconciliation and on-demand rebuilds.
4. Update [AN-S-3086](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/000_draft/AN-S-3086@2-draft-SWD--publish-and-query-the-import-graph-through-workbench.md) for persisted parsed imports.
5. Update [AN-S-1363](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-1363@12-draft-SWD--keep-duckdb-projection-ownership-in-the-existing-server.md) for disk-backed temporary results.
6. Update [AN-S-1366](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-1366@19-draft-QA--query-native-sql-results-and-typed-relation-expansion.md) for acceptance.
7. Update Policy Drafts AN-S-3156@1 and AN-S-3157@1 for dependent
   rebuilds and the same Operator controls in Workbench, Console, and MCP.
8. Update Realization Graph Drafts AN-S-3083@2, AN-S-3086@2, and
   AN-S-3087@2. Define Package identity and Test Package in AN-S-3004@1.
   Apply the test Relation rule from Current AN-S-3014@2.

## Definition of Done

The Spec covers both objectives. Verify disk-backed projections and results,
a rebuild from each Operator surface, and folder-derived test Relations
for Packages without a Spec Binding.

## Status

The rebuild and Realization Graph review fixes passed verification in a
disposable Workbench image. The Spec remains in Draft.
Citation migration requires the native `REFERENCES` Relation and a native
binding for the legacy proposal.

## References

[AN-T-2915](../done/AN-T-2915-EPIC--deliver-the-module-and-package-import-graph.md)

---
atom_family: TKT
atom_id: AN-T-2219
container:
  atom: AN-T-2070
priority: 2
context:
  template: task
state:
  status: archived
  version: 3
  updated_at: '2026-11-13T10:37:03.851577+00:00'
---
## Summary

Preserve Archive coverage and incremental indexing

## Work

1. Update RMEDO for reread coverage, incremental refresh, background audit preparation, and access to queryable ANECHOIC runtime data through DuckDB tables and `query_run`. Inventory the custom lookup indexes and identify which existing tables can replace them.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record. Cover Atom metadata, relations, live Runs, query history, and diagnostics.
3. Implement and verify table access for the reviewed data. Replace custom lookup indexes with table queries wherever the table can serve the lookup.
4. Implement and verify compact Archive allocation lookups. Check the maximum Archived Version for IDs with a Current Atom or Draft, and the maximum Archived Atom number per Role across all archived IDs. Verify allocation with Archive bodies unloaded.
5. Verify selected Archives remain queryable on demand, ordinary refresh stays targeted, and performance guards pass. Use the existing Atom ID and Version comments to find the implementing modules and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/source_reader.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP/workbench_tools.py`

## Details

Implemented and verified Archive allocation metadata, Relations, live Lifecycle Runs, query history, and gateway diagnostics through Workbench SQL. The Archive catalog stores filename metadata and leaves bodies on demand. The disposable Docker gate passed 20 tests, including performance and resource guards. Single-file changes took 0.25–0.33 s. A batch of 500 updates took 5.69 s.

Current RMED updates are CA-R-2723@7, CA-R-2903@8, CA-M-464@18, CA-D-672@24 and CA-E-681@7. Review the competing CA-R-2728 Drafts before publishing the SQL Requirement update. Review the remaining duplicate-carrier selection index separately because source validation uses it before Atom rows are published. The live MCP is still on the previous image.

---
atom_family: SPEC
atom_id: AN-S-1362
container:
  component: C43
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-11-04 18:38:27 +0400
---

## Summary

Place the DuckDB Projection in rebuildable runtime state

## Claim scope

The Project-local DuckDB runtime files, bundled dependencies and container delivery.

## Claim

### Prose Claim

Deliver the rebuildable DuckDB database at `.anechoic_runtime/workbench/projection.duckdb` in the selected repository. Keep internal materialized query results and owned spill data in that runtime directory. Rebuild source tables and clear old results at startup. Do not store source-byte copies, intermediate schema files or a second source of truth.

Expose only `main.atoms` and `main.scope_units` as public source tables. Internal graph mappings and generated result tables are disposable implementation state. Source files remain authoritative and unchanged by queries.

Bundle DuckDB `2.0.0` and its compatible DuckPGQ extension in the existing application image. Load the extension and grammar at trusted startup without downloading it at runtime. Disable external access and lock public configuration after startup. Admit native read queries only; trusted internal source refresh and result materialization use native write transactions with COMMIT. Do not add application retries, rollback or automatic recovery.

Build Svelte + TypeScript + Vite assets during image construction and serve the static output through Python. No Node server is needed at runtime. Deliver `/anechoic/workbench`, `/anechoic/mcp` and `/anechoic/health` on the configured listener.

The current Project container has a `1536m` memory budget. Keep query delivery bounded and let DuckDB spill within the owned runtime directory. Measure real-repository queries and refreshes against this budget; increasing RAM alone is not a substitute for paging. Report storage and engine errors explicitly. A failed owner requires an explicit restart.

Include the locked `pytz` dependency in the Workbench runtime group so native DuckDB timestamp-with-time-zone results can be fetched and encoded as ISO strings.

Exclude the frontend’s local `node_modules` dependency cache from release packages. Deliver its package manifest, lockfile and source, and build production assets in the image. Dependency-cache symlinks are not authored package input.

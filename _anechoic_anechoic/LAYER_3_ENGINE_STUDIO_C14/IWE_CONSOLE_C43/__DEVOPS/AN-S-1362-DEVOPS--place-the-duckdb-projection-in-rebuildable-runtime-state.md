---
atom_family: SPEC
atom_id: AN-S-1362
structure:
  container:
    component: C43
  tier: 4
context:
  lens: DevOps
relations:
  REFERENCES:
  - AN-S-3116@1
  - AN-S-1351
state:
  status: active
  version: 18
  updated_at: '2026-11-20T16:34:57.901983+00:00'
---

## Summary

Place the DuckDB Projection in rebuildable runtime state

## Claim scope

The Project-local DuckDB runtime files, bundled dependencies and container delivery.

## Claim

### Prose Claim

Deliver the rebuildable DuckDB database at `.anechoic_runtime/workbench/projection.duckdb` in the selected repository. Keep all native Workbench tables in that database, including temporary result and runtime observation tables. Keep spill data in the same runtime directory. Validate and reconcile retained native projections at normal startup before serving queries. Clear prior result tables and IDs at startup. Do not store source-byte copies, intermediate schema files or a second source of truth.

Expose `main.atoms` as a public source table and `main.change_log` as the technical watcher log. Legacy Workbench also exposes `main.scope_units`; native Workbench uses its native inventory. Internal graph mappings and generated result tables are disposable implementation state. Source files remain authoritative and unchanged by queries.

Transient result tables remain disposable state; the shared backend owner controls their retention and release.

Read native Workbench settings from the selected Project Manifest at startup. Legacy Workbench reads the editable `.anechoic_runtime/anechoic_runtime_settings.toml` at startup. For example:

```toml
[workbench]
result_ttl_seconds = 3600
```

`result_ttl_seconds` must be a positive integer; a missing file uses the 3,600-second default for this delivery, while an existing invalid file is a startup configuration failure reported on stderr rather than silently defaulted. An explicit `workbench_restart`/reread is required to apply an edited file; no hot reload is required. The runtime settings file is outside the watcher `control_root` and does not create a `change_log` event. MCP setting editing and new configuration Tools are deferred.

Bundle DuckDB `2.0.0` and its compatible DuckPGQ extension in the existing application image. Load the extension and grammar at trusted startup without downloading it at runtime. Disable external access and lock public configuration after startup. Admit native read queries only; trusted internal source refresh and result materialization use native write transactions with COMMIT. Roll back failed SQL writes. Add no application retry or automatic recovery.

Build Svelte + TypeScript + Vite assets during image construction and serve the static output through Python. No Node server is needed at runtime. Deliver `/anechoic/workbench/<project_name>`, `/anechoic/mcp` and `/anechoic/health` on the configured listener.

The current Project container has a `1536m` memory budget. Keep query delivery bounded and let DuckDB spill within the owned runtime directory. Measure real-repository queries and refreshes against this budget; increasing RAM alone is not a substitute for paging. Report storage and engine errors explicitly. A failed owner requires an explicit restart.

Include the locked `pytz` dependency in the Workbench runtime group so native DuckDB timestamp-with-time-zone results can be fetched and encoded as ISO strings.

Exclude the frontend’s local `node_modules` dependency cache from release packages. Deliver its package manifest, lockfile and source, and build production assets in the image. Dependency-cache symlinks are not authored package input.

Keep delivered service implementation, retained rebuildable database/index state and disposable indexing/build scratch separate from governed sources. Retained derived state remains non-authoritative and records its source-frontier references. Apply the existing Project Temporary State boundary to disposable scratch and build intermediates; keep the database, internal results and owned spill data at their declared Workbench runtime location. These storage choices grant no source-mutation capability.

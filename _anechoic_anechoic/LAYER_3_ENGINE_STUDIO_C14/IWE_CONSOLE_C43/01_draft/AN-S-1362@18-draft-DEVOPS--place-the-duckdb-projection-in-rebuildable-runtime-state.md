---
atom_family: SPEC
atom_id: AN-S-1362
container:
  component: C43
tier: 4
context:
  lens: DevOps
state:
  status: draft
  version: 18
  updated_at: '2026-11-14T00:32:41.337706+00:00'
---
## Summary

Place the DuckDB Projection in rebuildable runtime state

## Claim

### Prose Claim

Deliver the rebuildable DuckDB database and its dependencies within the
selected Project's Workbench runtime and application image.

## Details

- Source files remain authoritative and unchanged by queries.
- Report storage and engine errors explicitly. A failed owner requires
  an explicit restart.

### Runtime storage

- Store the database at `.anechoic_runtime/workbench/projection.duckdb`.
  Keep internal result tables and owned spill data in that runtime directory.
- Startup rebuilds source tables and clears old results. The shared owner
  controls retention and release. Results and graph mappings are disposable.
- Deliver `main.atoms` and `main.scope_units` as public source tables and
  `main.change_log` as the technical watcher log.
- Retained database and index state records source-frontier references.
  Use the Project Temporary State boundary for disposable build/index scratch.
- Keep authored sources, service implementation, and derived state separate.
  Keep source-byte copies and intermediate schema files out of runtime storage.

### Startup settings

- Use the Workbench TTL delivered by CA-D-725. Report invalid settings on stderr.
- Apply file edits after explicit `workbench_restart` or reread.
- The settings file is outside the watcher root and adds no `change_log` event.
- MCP settings editing and new configuration Tools remain deferred.

### Application image

- Bundle DuckDB `2.0.0` and compatible DuckPGQ. Load the extension and grammar
  at trusted startup from the image.
  - Disable external access and lock public configuration after startup.
  - Public input uses native reads. Trusted refresh and result materialization
    use native write transactions with COMMIT.
  - Application retries, rollback, and automatic recovery are outside this delivery.
- Include locked `pytz` for ISO encoding of timestamp-with-time-zone results.
- Build Svelte, TypeScript, and Vite assets into the image. Python serves
  the static output. Node is build-only.
  - Deliver frontend source, package manifest, and lockfile. Exclude
    `node_modules` and dependency-cache symlinks from release input.
- Serve `/anechoic/workbench/<project_name>`, `/anechoic/mcp`, and
  `/anechoic/health` on the configured listener.

### Resource budget

- The current Project container has a `1536m` memory budget.
- Use bounded query delivery, paging, and spill in the owned directory.
- Measure real-repository queries and refreshes against the budget.

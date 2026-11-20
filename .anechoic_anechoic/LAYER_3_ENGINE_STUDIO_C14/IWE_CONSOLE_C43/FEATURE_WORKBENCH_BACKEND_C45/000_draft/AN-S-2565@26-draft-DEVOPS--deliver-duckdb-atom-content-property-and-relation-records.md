---
identity:
  atom_id: AN-S-2565
context:
  container:
    component: C45
  tier: 4
  lens: DevOps
state:
  status: draft
  version: 26
  updated_at: '2026-11-13T22:33:10.642883+00:00'
---
## Summary

Deliver DuckDB Atom, Content Property, and relation records

## Claim scope

The Workbench DuckDB Projection and its query interfaces.

## Claim

### Prose Claim

#### Graph-source tables

The file-backed DuckDB Projection exposes `atoms` and `scope_units` through `query_schema` and `query_run`. They are its graph-source tables.

- `atoms` exposes the carrier path and filename, lifecycle group (Current, Draft, Backlog or loaded Archive), and exact reference. Archive rows use the requested Scope Unit and Role folders under CA-D-718. CA-D-723 specifies the Atom row contract.
- `scope_units` exposes declared name, ID, parent, label and order; Current structural source path and Version; native Relations; and a deterministic row hash excluding `hash`.
- DuckPGQ uses typed Atom and Scope Unit identities and declared labels. It is derived implementation state, not another table or authority.

#### Other query tables

- `relations` exposes the same typed direct and derived edges as DuckPGQ.
- `archive_version_max` and `archive_role_max` expose allocation metadata while Archive bodies remain unloaded.
- `live_runs` exposes Project-scoped lifecycle Run ID, session ID, Tool and Status as observed at query submission. `query_log` exposes retained query attempts.
- `runtime_diagnostics` exposes bounded Project gateway health observations with operation and outcome. Raw stderr, input payloads and pending Run input are excluded.
- `change_log` and the audit tables under CA-D-715 are queryable derived metadata, not graph sources or sources of truth.

#### Schema and storage

Column names use dotted lowercase snake_case paths. Mode 1 exposes declared Header and Content; enabled Mode 2 exposes observed raw Header paths and declared Content. `header.context.container` is the Mode 2 grouping-node JSON exception. Whole Header, Markdown and property buckets, short aliases and second source tables are not exposed. Arbitrary CFEL and prose are not evaluated.

The selected `workbench_schema.json` is delivered with the image. Internal mappings and results, database and spill files, selected schema and incremental snapshots are under the Workbench runtime directory. Source-byte, frontmatter and intermediate copies are not retained.

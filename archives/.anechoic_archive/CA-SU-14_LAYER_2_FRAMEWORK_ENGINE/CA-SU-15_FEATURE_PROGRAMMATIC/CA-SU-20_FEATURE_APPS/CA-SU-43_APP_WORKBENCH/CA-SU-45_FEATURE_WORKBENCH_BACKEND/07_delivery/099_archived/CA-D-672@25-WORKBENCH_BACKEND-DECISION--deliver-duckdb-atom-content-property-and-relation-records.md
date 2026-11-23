---
identity:
  atom_id: CA-D-672
  ref_id: CA-D-672@25
context:
  container:
    scope_unit: CA-SU-45
  role: Delivery
  form: Decision
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//ANECHOIC <+ Projection
    - ANECHOIC_MODEL <+ Projection
  tier: 4
relations:
  delivery_for:
  - CA-R-2723
  - CA-R-2726
  - CA-R-2724
  - CA-R-3132
  IS_REPLACEMENT_FOR:
  - CA-D-672
state:
  status: archived
  version: 25
  updated_at: '2026-11-13T21:06:05.418437+00:00'
destination:
  file:
    name: CA-D-672@25-WORKBENCH_BACKEND-DECISION--deliver-duckdb-atom-content-property-and-relation-records.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/07_delivery/099_archived
current_scope_unit: WORKBENCH_BACKEND
claim_target_scope_unit: WORKBENCH_BACKEND
author: Anatoly Maslennikov
---
## Summary

Deliver DuckDB Atom, Content Property, and relation records

## Claim scope

The derived `atoms` and `scope_units` tables and their complete parsed Header, Markdown heading paths, nested values, and materialized outgoing Relations.

## Claim

### Prose Claim

Deliver a file-backed DuckDB Projection. Expose `atoms` and `scope_units` as its graph-source tables through `query_schema` and `query_run`.

- `atoms` exposes the carrier locator, lifecycle group (Current, Draft, Backlog or loaded Archive) and exact reference. Archive rows come from the Scope Unit and Role folders selected under CA-D-718.
- `scope_units` exposes the declared name, ID, parent, label and order, the Current structural source path and Version, native Relations and a deterministic row hash that excludes the hash field.
- `relations` exposes the same typed direct and derived edges used by DuckPGQ. The graph representation uses typed Atom and Scope Unit identities and declared labels. The DuckPGQ graph is derived implementation state. It has no separate table or authority.
- `archive_version_max` and `archive_role_max` expose allocation metadata while Archive bodies remain unloaded.
- `live_runs` exposes the selected Project's Run ID, session ID, Tool and Status as observed at query submission. `query_log` exposes retained query attempts.
- `runtime_diagnostics` exposes the Project gateway's bounded health observations, including operation and outcome. Exclude raw stderr, input payloads and pending Run input.
- `change_log` and the audit tables delivered under CA-D-715 expose derived metadata. They are neither graph sources nor sources of truth.

Use dotted lowercase snake_case column paths. Expose model-declared Header and Content in Mode 1, and observed Header and declared Content in Mode 2. Use JSON for `header.context.container` as the Mode 2 grouping-node exception. Omit raw Header, Markdown and whole-property buckets, short aliases and any second source tables. Do not evaluate arbitrary CFEL or prose.

Package the selected `workbench_schema.json` with the image. Place internal mappings, result tables, database and spill files, the selected runtime schema and incremental snapshots under the Workbench runtime directory.

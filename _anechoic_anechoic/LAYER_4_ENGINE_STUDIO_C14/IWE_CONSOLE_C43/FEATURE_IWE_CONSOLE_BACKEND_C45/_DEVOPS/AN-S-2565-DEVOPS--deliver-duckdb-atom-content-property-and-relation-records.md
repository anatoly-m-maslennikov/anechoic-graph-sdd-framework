---
atom_family: SPEC
atom_id: AN-S-2565
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C45
tier: 4
context:
  lens: DevOps
state:
  status: active
  version: 28
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Deliver DuckDB Atom, Content Property, and relation records

## Claim scope

The derived `atoms` and `scope_units` tables and their complete parsed Header, Markdown heading paths, nested values, and materialized outgoing Relations.

## Claim

### Prose Claim

Read governed sources directly through the Current-model parser into a file-backed DuckDB Projection. Expose `atoms` and `scope_units` as graph-source tables. Technical `change_log` and the audit tables delivered under CA-D-715 are queryable derived metadata, not graph sources or sources of truth. Expose `relations`, `archive_version_max`, `archive_role_max`, `live_runs`, and `query_log` through `query_schema` and `query_run`. `relations` reads the same typed direct and derived edges as DuckPGQ. The Archive tables expose allocation metadata while bodies stay unloaded. `live_runs` shows Project-scoped lifecycle Run ID, session ID, Tool and Status as observed at query submission. `query_log` exposes the existing retained query attempts. `runtime_diagnostics` exposes the Project gateway’s bounded health observations, with operation and outcome fields. Keep raw stderr, input payloads and pending Run input out of those diagnostics. Internal mappings/results, database/spill, selected schema and incremental snapshots belong under the Workbench runtime directory. Do not retain source-byte/frontmatter/intermediate copies.

Parse complete YAML and actual Markdown heading paths, preserving missing/null/empty/scalar/list/map/false/zero distinctions and complete mapped content. Current structural Declarations/Delegations establish `scope_units`; Draft structural carriers remain atoms. Mode 1 exposes current-model declared Header/Content through the grouped adapter and accepted read aliases only; enabled Mode 2 exposes every observed raw Header path plus declared Content. Names use dotted lowercase snake_case paths. Header relations are one native `header.relations` JSON projection; `header.context.container` is the Mode-2 grouping-node exception. Do not expose whole Header/Markdown/property buckets, short aliases, second source tables or arbitrary CFEL/prose evaluation.

In refresh mode, generate and validate `workbench_schema.json` from Current Declarations. In existing mode, build with the checkout asset unchanged. Load the delivered asset at startup. Keep its Content schema and Mode 1 Header schema fixed; Mode 2 selects observed Header paths at cold start. Ordinary Atom edits and explicit rereads refresh data under the selected schema. The running service does not compile model declarations.

`atoms` identifies carrier path/filename, Current, Draft, Backlog or loaded Archive lifecycle, exact reference, typed `header.*`/`content.*`, native `header.relations` and deterministic row hash excluding `hash`. The `atoms` primary key is the physical pair `(relative_path, filename)`. Keep each readable matching carrier, including duplicate logical identities and revisions. Archive rows come from requested Scope Unit and Role folders under CA-D-718. `scope_units` identifies declared name/ID/parent/label/order, Current structural source path/version, native relations and the same hash rule. Use the Active Model for Relation names and derivation. Apply AN-S-3175 to Atom Relations. For admitted legacy carriers, use the CA-M-509 registry to normalize exact aliases or unique case-folded spelling once without changing source. Warn on ambiguity or case collisions and omit affected links. References remain typed references, and direct/derived counterparts refresh with their supporting source while source bytes/Versions do not change. DuckPGQ uses typed Atom/Scope Unit identities and declared labels only; it is derived implementation state, not another table or authority.

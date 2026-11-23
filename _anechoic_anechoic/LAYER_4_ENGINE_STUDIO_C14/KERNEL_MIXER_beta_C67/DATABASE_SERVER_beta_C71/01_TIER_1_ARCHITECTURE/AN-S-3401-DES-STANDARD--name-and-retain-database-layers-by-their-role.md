---
atom_family: SPEC
atom_id: AN-S-3401
container:
  component: C71
tier: 1
context:
  template: STANDARD
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-23T10:31:56.329107+00:00'
---
## Summary

Name and retain database layers by their role.

## Claim

### Prose Claim

Use these local prefixes, based on dbt terminology, for database objects:

- `src_`: raw captured input, including captured digests.
- `int_`: parsed or joined working projections.
- `mrt_`: published domain entities, graph data, and diagnostics.
- `biz_`: derived metrics and rollups.
- `ops_`: durable runtime records, including journal, query log, checkpoints, and generation hashes.

Use `mrt_real_graph_*` for Realization Graph nodes, edges, and evidence. Use `mrt_diag_*` for findings from admitted data.

Keep current failures from Atom capture, code scanning, and generation builds in `ops_ingestion_issues`. Record the source, error code, message, and any known file paths or Atom reference. Preserve published data when ingestion fails. Clear issues when the affected inputs pass recheck.

Publish the complete Atom projection as `mrt_atoms`. Provide filtered views for each native Atom family as `mrt_spec_atoms`, `mrt_ticket_atoms`, and `mrt_project_config_atoms`.

Publish Atom Graph relations as `mrt_atom_graph_relations` and native Atom references as `mrt_atom_references`. Publish one flow summary per Component and Action in `mrt_flow_actions`.

Name the private generation checkpoint `ops_generation_carrier_hashes`.

Use `stg_` only when a distinct first cleanup layer is warranted. Retain the `workbench_results` namespace for retained results.

Name digest fields for both subject and algorithm. For example, a file's `content_sha256` belongs with the file; `manifest_sha256` and generation checkpoints are operational records.

Store sizes in bytes. Convert units for presentation. Rebuild derived layers from their inputs, and preserve operational history and retained results according to their existing contracts.

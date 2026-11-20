---
identity:
  atom_id: AN-S-3086
context:
  container:
    component: C61
  tier: 2
  lens: SWD
state:
  status: "draft"
  version: 2
  updated_at: "2026-11-20T13:02:25.098064+00:00"
---

## Summary

Publish and query the Import Graph through Workbench

## Claim

### Prose Claim

Deliver this projection on the native Workbench query owner. In the selected Project Manifest, `runtime.workbench.import_graph` enables the projection when present as a mapping. Its optional `python_roots` is an ordered list of Project-relative roots and `include` is a list of Project-relative source files. Reconcile the retained import snapshot with the current Project at startup. Build it from source when no compatible snapshot exists. Use one existing `SourceWatcher` observer and event queue over the selected Project without overlapping roots. Filter its batches with the scan's admission rules and resolve both ends of a move. Route only import input changes to this projection. Keep Atom indexing and Spec Trace on their existing paths.

Parse added and edited files, scan new and moved subtrees, and remove facts from deleted paths. Re-resolve affected occurrences from the recorded specifiers when a source path or resolution input changes. Store the admitted file path, fingerprint, scan status, parser version, and raw import sites in the Workbench DuckDB file. Retain the written Module, imported name, relative level, line, and column. Reuse a parsed record when its fingerprint and parser version match. Reconcile source changes made while Workbench was stopped, then resolve from the current inventory and configuration. Remove stale import facts and registration before serving queries when the Import Graph is disabled. Scan and parse before taking the query lock. Publish each batch in one transaction on the existing Workbench DuckDB connection. On refresh failure, write an explicit error to stderr, discard the failed batch, and make no partial publication. Rebuild the Atom and import projections from the selected sources on a full rebuild.

| SQL relation | Contents |
| --- | --- |
| `import_nodes` | Node key, kind, language, local path and scan status where applicable, and Module ownership when known. Include inventoried Modules and identified Package and external Module targets. |
| `module_imports` | Occurrence key, source Module, resolved target if known, written specifier, line, column, resolution status, and type-only flag. |
| `import_edges` | One row per occurrence and directed pair, with source and target keys, occurrence key, and derived flag. |
| `package_imports` | A view that groups Package → Package edges and counts contributing occurrences. |

Register `import_nodes` as `ImportNode` vertices and `import_edges` as `Imports` edges in the existing `anechoic` property graph. Keep that registration when an Atom graph rebuild changes the relation layout. Admit the import relations in the active Workbench owner's public SQL schema for completion and the existing results grid. Supply read-only `SELECT` examples for outgoing and incoming queries at Module and Package level. Use the same Workbench results through `POST /anechoic/{project_name}/api/run` from a terminal. Let each result lead to the source occurrence by file and line.

## References

[Disk storage Decision AN-S-3116](../../FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-3116@1-draft-DES-DECISION--store-native-workbench-duckdb-data-on-disk.md), [Tier 1 Decision AN-S-3083](../DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md), [Spec Proposal CA-A-1467](../../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).

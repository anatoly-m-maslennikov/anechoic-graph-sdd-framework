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
  updated_at: "2026-11-20T16:02:36.482794+00:00"
---

## Summary

Publish and query the Import Graph through Workbench

## Claim

### Prose Claim

- Deliver this projection on the native Workbench query owner.
- Enable it when `runtime.workbench.import_graph` is a mapping in the selected Project Manifest.
- Its optional `python_roots` is an ordered list of Project-relative roots.
- Its `include` is a list of Project-relative source files.
- Reconcile the retained import snapshot with the current Project at startup.
- Build from source when no compatible snapshot exists.
- Use one existing `SourceWatcher` observer and event queue over the selected Project.
- Do not overlap watcher roots.
- Filter watcher batches with the scan admission rules and resolve both ends of a move.
- Route import inputs and test-directory changes to this projection.
- Keep Atom indexing and Spec Trace on their existing paths.
- Parse added and edited files, scan new and moved subtrees, and remove facts from deleted paths.
- Re-resolve affected occurrences from recorded specifiers when a source path or resolution input changes.
- Store admitted paths, fingerprints, scan status, parser version, and raw import sites in Workbench DuckDB.
- Retain each written Module, imported name, relative level, line, and column.
- Reuse parsed records when fingerprint and parser version match, except after a read issue.
- Retain each current source read issue with its path and message until a successful read or removal.
- On the next ordinary scan, read that source even if its fingerprint is unchanged.
- Add no automatic retry or recovery.
- Reconcile source changes made while Workbench was stopped.
- Then resolve from the current inventory and configuration.
- When the Realization Graph is disabled, remove stale import facts and registration before serving queries.
- Scan and parse before taking the query lock.
- Publish each batch in one transaction on the existing Workbench DuckDB connection.
- On refresh failure, write an explicit error to stderr and discard the failed batch.
- Make no partial publication on refresh failure.
- If a failed rebuild may have lost DuckPGQ registration, leave the owner unavailable until explicit restart.
- Return the error in each failed HTTP or MCP request.
- On a full rebuild, rebuild Atom and enabled import projections from the selected sources.
- A selected table rebuild also rebuilds its dependent tables, views, and graph registration.

| SQL relation | Contents |
| --- | --- |
| `import_nodes` | Node key, kind, language, local path and scan status where applicable. |
| `import_nodes` | Module ownership when known. |
| `import_nodes` | Include inventoried Modules and identified Package and external Module targets. |
| `import_nodes` | Use `package:local:<relative path>` for each local folder across all languages. |
| `import_nodes` | Set `package_type` to `Test Package` for the direct test directory. |
| `module_imports` | Occurrence key, source Module, resolved target if known, and written specifier. |
| `module_imports` | Line, column, resolution status, and type-only flag. |
| `import_edges` | One row per occurrence and directed pair. |
| `import_edges` | Source and target keys, occurrence key, and derived flag. |
| `package_imports` | View grouping Package → Package edges and counting contributing occurrences. |
| `test_edges` | Source Test Package key and target parent Package key for each direct test directory. |
| `tested_by_edges` | Source parent Package key and target Test Package key. |
| `import_read_issues` | Project-relative file path and error message for each current failed source read. |

- Derive `TESTS` from each direct `<full package folder name>__tests/` Package to its parent Package.
- Include the Relation when the parent has no Spec or Spec Binding.
- Publish both directions with the same Package keys as imports.
- Register `test_edges` as `TESTS` and `tested_by_edges` as `IS_TESTED_BY` in the `anechoic` property graph.
- Remove the Relations when the direct directory is removed or moved.
- Register `import_nodes` as `ImportNode` vertices and `import_edges` as `Imports` edges in `anechoic`.
- Keep that registration when an Atom graph rebuild changes the relation layout.
- Admit Realization Graph tables in the active Workbench owner's public SQL schema.
- Make them available for completion and the existing results grid.
- Supply read-only `SELECT` examples for outgoing and incoming queries at Module and Package level.
- Use the same Workbench results through `POST /anechoic/{project_name}/api/run` from a terminal.
- Let each result lead to the source occurrence by file and line.

## References

[Disk storage Decision AN-S-3116](../../FEATURE_WORKBENCH_BACKEND_C45/000_draft/AN-S-3116@1-draft-DES-DECISION--store-native-workbench-duckdb-data-on-disk.md), [Tier 1 Decision AN-S-3083](../DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md), [Spec Proposal CA-A-1467](../../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md).

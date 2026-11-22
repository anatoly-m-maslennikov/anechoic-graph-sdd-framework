---
atom_family: SPEC
atom_id: AN-S-3086
container:
  component: C61
tier: 2
context:
  lens: SWD
relations:
  IS_REFERENCE:
  - AN-S-3116@1
  - AN-S-3083
  - AN-T-2928@1-draft
state:
  status: "active"
  version: 9
  updated_at: "2026-11-22T10:36:42.735857+00:00"
---

## Summary

Publish and query the Import Graph through Workbench

## Claim

### Prose Claim

- Deliver this projection on the native Workbench query owner.
- Enable it by default. Set `runtime.workbench.import_graph` to `false` in the selected Project Manifest to disable it.
- Its optional `python_roots` is an ordered list of Project-relative roots.
- Its optional `python_image_imports` declares exact module names per
  Project-relative Python source file. Use it for execution in a previous
  runtime image. When a declared module has no local target, retain its
  occurrence and record it as a declared previous-image dependency.
- Its `include` is a list of Project-relative source files.
- Reconcile the retained import snapshot with the current Project at startup.
- Build from source when no compatible snapshot exists.
- Use one existing `SourceWatcher` observer and event queue over the selected Project.
- Do not overlap watcher roots.
- Filter watcher batches with the scan admission rules and resolve both ends of a move.
- Route import inputs and test-directory changes to this projection.
- Refresh the Atom projection for Carrier changes, including when the Import Graph is disabled. Keep Spec Trace on its existing path.
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
| `import_nodes` | Use `package:local:<relative path>` for each folder with a direct executable. |
| `import_nodes` | Set `package_type` to `Test Package` for the direct test directory. |
| `module_imports` | Occurrence key, source Module, resolved target if known, and written specifier. |
| `module_imports` | Line, column, resolution status, and type-only flag. |
| `import_edges` | One row per occurrence and directed pair. |
| `import_edges` | Source and target keys, occurrence key, and derived flag. |
| `package_imports` | View grouping Package → Package edges and counting contributing occurrences. |
| `test_edges` | Source Test Package key and target parent Package key or Component ID. |
| `tested_by_edges` | Source parent Package key or Component ID and target Test Package key. |
| `import_read_issues` | Project-relative file path and error message for each current failed source read. |

- Derive `TESTS` from a direct `<parent folder name>__tests/` Package to its parent Package or declared Component.
- Include the Relation when the parent has no Spec or Spec Binding.
- Publish both directions with the same Package keys as imports.
- Register Package endpoints as `TESTS` and `IS_TESTED_BY` in `anechoic`.
- Register Component endpoints as `TESTS_COMPONENT` and `COMPONENT_IS_TESTED_BY` against existing Component references.
- Remove the Relations when the direct directory is removed or moved.
- Register `import_nodes` as `ImportNode` vertices and `import_edges` as `Imports` edges in `anechoic`.
- Keep that registration when an Atom graph rebuild changes the relation layout.
- Admit Realization Graph tables in the active Workbench owner's public SQL schema.
- Make them available for completion and the existing results grid.
- Supply read-only `SELECT` examples for outgoing and incoming queries at Module and Package level.
- Use the same Workbench results through `POST /anechoic/{project_name}/api/run` from a terminal.
- Let each result lead to the source occurrence by file and line.

## Package audit

Publish `package_audit` with one row for each local Package node, including Test Packages and Packages without a Spec.

- Report direct `__shared` and `__pub` executable filename markers independently.
- Report `missing_visibility_marker` on a tested Package with neither marker.
- Report `missing_test_target` on a Test Package whose parent qualifies as neither Package nor Component.
- Report canonical `__spec_bind.yaml` presence and whether the binding is missing, invalid, empty, or valid. Use the full Package folder name for the sidecar.
- Check every `implements` and `applies` pin against the exact active Spec revision. Resolve legacy pins only through an unambiguous exact alias.
- Report each failed pin and its reason. Distinguish archived, missing, ambiguous, and non-Spec references. Leave the active-pin result unknown if there are no valid pins.
- For a Component Seed, report its active Component Seed Manifest reference and whether `implements` pins that exact revision. Leave Contract coverage unknown when the Component Seed Manifest or ownership cannot be established.
- Report an invalid Component Seed Manifest or unreadable ownership to stderr. Keep the other Package audit facts available.
- Contract coverage records a trace to the Component Seed Manifest. Evidence from implementation and tests establishes Contract satisfaction.
- Refresh on admitted source, sidecar, and Spec changes. Publish in the same DuckDB transaction as the changed projection and rebuild with its dependencies.

---
identity:
  atom_id: AN-T-2928
context:
  container:
    component: C14
  tier: 3
  template: Spec Proposal
state:
  status: draft
  version: 1
  updated_at: '2026-11-19T18:46:02.994946+00:00'
---
## Summary

Derive a module and package import graph from Project source

## Proposal

Extend the existing Workbench index and DuckPGQ property graph `anechoic` with static imports. Select executable source from the Project root, extract import declarations, and publish the results to the Workbench DuckDB database. Use `SourceWatcher` to keep the results current. Show Module → Module, Module → Package, Package → Module, and Package → Package dependencies in Workbench and through the Workbench SQL endpoint from a terminal. The result is a dependency view of the Anechoic Project's Realization Graph (CA-R-1616, CA-R-1620, CA-R-1621).

### Workbench integration

Workbench already publishes `implementation_objects` and `implementation_rmedo` to DuckDB. The scanner selects files under the Workbench pilot, labels their ancestor directories as packages, and reads explicit RMeDO references from sidecar files. The Atom source reader selects Markdown carriers from the control root. The Project-wide source inventory and language import extractor are new work. [Spec trace scanner](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/spec_trace.py), [Atom source reader](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/source_reader.py)

Extend `SourceWatcher` subscriptions beyond the Workbench pilot when the import graph is enabled. Use one observer and one event queue. In `ServiceIndexing._index`, route each existing batch to the Atom, spec-trace, and import update paths according to the files that changed. Use both the old and new paths to classify moves. Apply the same file selection to the initial scan and watcher events, and include configuration inputs that affect import resolution. [SourceWatcher](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/source_watcher.py), [Indexing loop](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service_indexing.py), [Graph store](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/graph_store.py)

The native Workbench query owner builds its own startup projection and filters its public SQL schema. Route the existing watcher batches and the shared import table publisher into the active query owner for the selected Project. Register the import relations in that owner's public schema. [Native query owner](../../../../LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/native_query.py)

### Source selection

Scan recursively from the Project root. Use the live working tree so the graph includes local source edits. List Project-authored executable source by language, file type, or shebang. Include modules, package initializers, scripts, and test code even when they lack the executable permission bit. Record the inclusion and exclusion rules with the snapshot. Exclude dependency installs, generated or archived copies, caches, and runtime output, including copies that Git tracks. Keep traversal within the Project root. Respect Project exclusions and allow explicit selection of authored files that an ignore rule would otherwise omit.

Start import extraction with Python's standard-library AST parser. Include JavaScript, TypeScript, and Svelte script blocks when their parsers are available in the deployed extraction runtime. The current Docker image uses Node for the frontend build and runs the backend in a separate Python stage. Inventory `.js`, `.mjs`, `.ts`, and `.svelte` files from the first scan. Mark every recognized file with no available parser as unsupported. Keep files with zero imports, parse errors, or read errors in the inventory so that operators can distinguish each case. [Workbench Dockerfile](../../../../LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/Dockerfile)

### Import facts

Read each file as text. Extract direct source-level import declarations and keep their Project-relative file path, line, and written module specifier. Include Python `import` and `from … import` statements, including relative imports, and JavaScript and TypeScript static `import` declarations, including side-effect imports. Include declarations inside conditional blocks where the language permits them. Each row records source syntax, so it does not prove execution. Record an occurrence as type-only when the entire import is type-only. Keep a declaration with both value and type bindings as one value import occurrence. Exclude export and re-export declarations, dynamic loads, and other execution relationships. Never execute the scanned source.

Use the language's declared package boundaries, source roots, and alias mappings to resolve internal targets. Use explicit, ordered Python source roots for the selected launch profile. The MCP launcher adds source roots for local absolute imports such as `operation_error_boundary`. Apply the declared TypeScript resolution mode for Workbench sources. [MCP entry point](../../../../LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/entrypoint.py), [Workbench TypeScript settings](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/tsconfig.json)

Preserve separate identities for modules in different locations with the same name. For package queries, group Python modules by the top-level package under the selected source root. Group JavaScript, TypeScript, and Svelte modules by the nearest package manifest. Use the declared package identity for identified external packages. Leave package ownership unset when the evidence does not identify a package. For Python `from` imports, only use an imported name as a submodule target when static resolution supports that choice. Record a target as external when the selected environment or package declarations identify it as such. Keep ambiguous and unresolved imports with their written specifiers and resolution status. An import occurrence starts at the Module whose file contains the statement. The resolved target is a Module or Package. For a Package initializer, attribute the statement to its source file and use that file's Package to derive Package-level dependencies. Incoming queries show which Modules or Packages import the target.

### Relation directions

| Relation | Source of the relation |
| --- | --- |
| Module → Module | The import resolves to a Module. |
| Module → Package | The import resolves to a Package, or the target Module belongs to that Package. |
| Package → Module | The source Module belongs to a Package and the import resolves to a Module. |
| Package → Package | The source Module belongs to a Package. The import resolves to a Package or to a Module with a known Package. |

For each import occurrence, derive each applicable pair once. A Module without a known Package still appears in Module-level results. Keep imports within a Package and cycles visible. Use the original occurrence to show the importing file, line, and written specifier for every pair. Mark edges that use a Module's Package as derived.

### DuckDB and display

| Relation | Rows |
| --- | --- |
| `import_nodes` | One row per inventoried Module or identified Package or external Module. Store the node key, kind, language, and the local path and scan status where applicable. Store the Module's Package key when known. |
| `module_imports` | One row per import occurrence. Store the occurrence key, source Module key, target key when resolved, written specifier, line, column, resolution status, and whether the import is type-only. |
| `import_edges` | One row per occurrence and directed pair from the four cases above. Store the source and target keys, occurrence key, and whether the edge is derived. Keep unresolved and ambiguous imports in `module_imports` so operators can inspect them. |
| `package_imports` | A SQL view that groups Package → Package edges and counts their contributing occurrences. |

Register `import_nodes` and `import_edges` in the existing `anechoic` property graph declaration in `graph_store.py`. Use the node kind to query any of the four endpoint combinations. File edits update the import rows. An Atom graph rebuild registers the import tables again as part of the same graph declaration. [Property graph declaration](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/graph_store.py)

Build the first import snapshot from the selected source during the existing full index in `ServiceRefresh`. Then update the import projection from watcher batches. Parse added and edited files. Remove facts for deleted paths and scan new or moved subtrees. If a source path or resolution setting changes, resolve affected targets again from the recorded import specifiers. This covers an unchanged importer whose target was added, moved, or deleted. [Full index](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service_refresh.py), [Watcher batches](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service_indexing.py)

Record the source selection, input fingerprints, and parser and resolver versions with the snapshot. Scan and parse before taking the DuckDB query lock. Apply each batch in one transaction on the current Workbench connection. If a refresh fails, write an explicit error to stderr and make no partial publication. On a full rebuild, recreate both projections from the selected sources. [Transaction pattern](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/service_refresh.py), [Reread](../../../../LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/workbench_tools.py)

Add these relations to Workbench's public SQL schema so the existing editor can suggest them and the existing results grid can display them. For terminal use, provide sample `SELECT` queries through the same read-only Workbench HTTP `POST /anechoic/{project_name}/api/run` route. Provide queries for outgoing imports and incoming importers at both levels. Keep module import occurrences available for inspection by file and line. [SQL schema](../../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/query_schema.py), [Workbench HTTP route](../../../../LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/workbench_web.py)

### Acceptance checks

- Scan a test Project with a module that lacks the executable bit, a file with no imports, an unsupported script, an unreadable or invalid file, and a generated copy. Verify the inventory, exclusions, and scan statuses. Verify that unreadable and invalid files produce explicit path-specific errors on stderr and publish no import facts for the affected file. Keep unsupported scripts as ordinary inventory statuses.
- Check absolute, relative, aliased, conditional, external, ambiguous, and unresolved imports. Verify that type-only imports are marked and that comments, exports, and dynamic loads produce no edges. Check that repeated imports keep their own source locations.
- Resolve `operation_error_boundary` from the MCP entry point under its declared source roots. When frontend extraction is available, check that `App.svelte` resolves local `.svelte` and extensionless imports and distinguishes mixed and type-only imports.
- Use a Module in one Package that imports a Module in a second Package. Verify all four relation types and trace each to the same source occurrence. Also check a direct Package import, a Module with unknown Package ownership, and two imports of the same target on different lines. Compare incoming and outgoing query results in Workbench and through the Workbench HTTP route. Verify that cycles remain visible.
- Edit, add, move, and delete source files outside the Workbench pilot. Verify that the existing watcher updates import rows. Add a missing target, then remove it. Verify that the unchanged importer changes resolution without another parse. Verify that an Atom edit and a generated-file edit cause no import parsing. Verify that each admitted source event comes through the existing watcher queue.
- Query both Atom edges and import edges with `GRAPH_TABLE` before and after changing the Atom relation layout. Force an import publication failure and verify that it writes an explicit error to stderr and makes no partial publication.

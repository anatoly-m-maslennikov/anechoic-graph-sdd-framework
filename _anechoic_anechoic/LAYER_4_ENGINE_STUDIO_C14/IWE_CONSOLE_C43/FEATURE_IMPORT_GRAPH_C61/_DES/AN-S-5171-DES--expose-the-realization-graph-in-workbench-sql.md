---
atom_family: SPEC
atom_id: AN-S-5171
container:
  component: C61
tier: 2
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: "2026-11-27T18:09:40.995150+00:00"
---

## Summary

Expose the Realization Graph in Workbench SQL

## Claim

Apply this contract to the selected Project's Realization Graph.

| SQL relation | Contents |
| --- | --- |
| `import_nodes` | Node key, kind, language, local path and scan status where applicable. |
| `import_nodes` | Module ownership when known. |
| `import_nodes` | Include inventoried Modules and identified Package and external Module targets. |
| `import_nodes` | Use `package:local:<relative path>` for each local Package admitted under AN-S-3159. |
| `import_nodes` | Use `package_type` from its admitted kind under AN-S-4838. |
| `module_imports` | Occurrence key, source Module, resolved target if known, and written specifier. |
| `module_imports` | Line, column, resolution status, and type-only flag. |
| `import_edges` | One row per occurrence and directed pair. |
| `import_edges` | Source and target keys, occurrence key, and derived flag. |
| `package_imports` | View grouping Package → Package edges and counting contributing occurrences. |
| `test_edges` | Source Test Package key and target parent Package key or Component ID. |
| `tested_by_edges` | Source parent Package key or Component ID and target Test Package key. |
| `import_read_issues` | Project-relative file path and error message for each current failed source read. |

- Use AN-S-3014 and AN-S-3159 for Test Package Relations. Publish both directions with the same Package keys as imports, even when no Spec Binding exists.
- Register Package endpoints as `TESTS` and `IS_TESTED_BY` in `anechoic`.
- Register Component endpoints as `TESTS_COMPONENT` and `COMPONENT_IS_TESTED_BY` against existing Component references.
- Recompute affected test edges when the directory, Package qualification, or Component ownership changes.
- Register `import_nodes` as `ImportNode` vertices and `import_edges` as `Imports` edges in `anechoic`.
- Keep that registration when an Atom graph rebuild changes the relation layout.
- Admit Realization Graph tables in the active Workbench owner's public SQL schema.
- Make them available for completion and the existing results grid.
- Supply read-only `SELECT` examples for outgoing and incoming queries at Module and Package level.
- Use the same Workbench results through `POST /anechoic/{project_name}/api/run` from a terminal.
- Let each result lead to the source occurrence by file and line.

---
atom_family: TKT
atom_id: AN-T-2915
container:
  component: C43
priority: 2
context:
  template: task
  label: Epic
state:
  status: done
  version: 6
  updated_at: '2026-11-20T23:12:09.705525+00:00'
---
## Summary

Deliver the module and package import graph

## Objective

Specify the Import Graph Component and its architecture.

## Work

1. Add the [Import Graph Component Manifest](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/AN-S-3082-SPEC-COMPONENT_MANIFEST--declare-import-graph.md).
2. Add the [Tier 1 Decision for the Import Graph architecture](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/__DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md).
3. Add the [source selection and static import extraction Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/__SWD/AN-S-3084-SWD--select-source-files-and-extract-static-imports.md).
4. Add the [import resolution and relation semantics Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/__DES/AN-S-3085-DES--resolve-imports-and-derive-module-and-package-relations.md).
5. Add the [Workbench refresh, DuckDB publication, and query Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/__SWD/AN-S-3086-SWD--publish-and-query-the-import-graph-through-workbench.md).
6. Add the [Import Graph acceptance Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/__QA/AN-S-3087-QA--verify-the-import-graph-through-public-workbench-queries.md).
7. Update the [Workbench SQL and graph acceptance Atom](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/__QA/AN-S-1366-QA--query-native-sql-results-and-typed-relation-expansion.md).

## Definition of Done

The Component Manifest, Tier 1 Decision, and supporting Spec Atoms cover the reviewed design.

## Status

The Spec has been reviewed against the existing Spec and code. The native implementation passed focused checks for all four relations, Workbench and terminal queries, watcher updates, and failed publication.

The seven Spec Atoms are Current. Workbench `0.4.4.54` passed the full release gate. Live SQL and DuckPGQ queries returned all four Module and Package relation types.

## References

[CA-A-1467@1-draft](../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md)

## Realization Graph Package Audit

Expose package visibility markers, Spec Binding presence and validity, exact active pin status, and Package Contract coverage in Workbench.

8. Update the Workbench publication and acceptance Specs with the Package audit.
9. Publish `package_audit` from the existing Package inventory, Spec Bindings, and current Specs.
10. Verify watcher refresh, persisted startup, and targeted rebuild through the public query interface.

The Package audit is complete when these checks pass against the implemented projection.

### Package audit verification

Eight native Workbench tests and six Spec Trace tests passed. The
end-to-end case checked watcher updates, invalid binding and Contract
inputs, targeted rebuild, and database reopen.

An isolated audit of the Project returned 75 local Package rows.
Each of the three declared Package Contracts had its exact active
Package Spec in `implements`.

## Recursive Package discovery

11. Update the Realization Graph Specs with language-independent Package discovery.
12. Publish and audit one Package per non-dot folder with an executable in its subtree.
13. Verify watcher updates, persisted startup, and existing import resolution.

The 26 focused tests and the separate polling-mode check passed.
An isolated Project run found 78 local Packages across 709 executable files.

## Direct Package discovery and Component tests

14. Update the Realization Graph Specs for direct executables and Component-level tests.
15. Publish Package and Component test targets and audit missing Package markers or test targets.
16. Verify import resolution, test Relations, watcher updates, and persistent startup.

The 27 focused tests and eight polling-mode startup tests passed.
The isolated Project projection found 65 Packages, 24 Package test links,
and five Test Packages without a target.

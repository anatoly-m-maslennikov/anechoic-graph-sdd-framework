---
atom_family: TKT
atom_id: AN-T-2915
structure:
  container:
    component: C43
  priority: 2
context:
  template: epic
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-20T21:51:08.544370+00:00"
---
## Summary

Deliver the module and package import graph

## Objective

Specify the Import Graph Component and its architecture.

## Work

1. Add the [Import Graph Component Manifest](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/AN-S-3082-SPEC-COMPONENT_MANIFEST--declare-import-graph.md).
2. Add the [Tier 1 Decision for the Import Graph architecture](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/DES/AN-S-3083-DES-DECISION--extend-workbench-with-the-import-graph.md).
3. Add the [source selection and static import extraction Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/SWD/AN-S-3084-SWD--select-source-files-and-extract-static-imports.md).
4. Add the [import resolution and relation semantics Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/DES/AN-S-3085-DES--resolve-imports-and-derive-module-and-package-relations.md).
5. Add the [Workbench refresh, DuckDB publication, and query Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/SWD/AN-S-3086-SWD--publish-and-query-the-import-graph-through-workbench.md).
6. Add the [Import Graph acceptance Spec](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_IMPORT_GRAPH_C61/QA/AN-S-3087-QA--verify-the-import-graph-through-public-workbench-queries.md).
7. Update the [Workbench SQL and graph acceptance Atom](../../../LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/FEATURE_WORKBENCH_BACKEND_C45/QA/AN-S-1366-QA--query-native-sql-results-and-typed-relation-expansion.md).

## Definition of Done

The Component Manifest, Tier 1 Decision, and supporting Spec Atoms cover the reviewed design.

## Status

The Spec has been reviewed against the existing Spec and code. The native implementation passed focused checks for all four relations, Workbench and terminal queries, watcher updates, and failed publication.

The seven Spec Atoms are Current. Workbench `0.4.4.54` passed the full release gate. Live SQL and DuckPGQ queries returned all four Module and Package relation types.

## References

[CA-A-1467@1-draft](../../../../.anechoic_legacy/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/02_analysis_and_advisory/000_draft/CA-A-1467@1-draft-FRAMEWORK_ENGINE-SPEC_PROPOSAL--derive-a-module-and-package-import-graph-from-project-source.md)

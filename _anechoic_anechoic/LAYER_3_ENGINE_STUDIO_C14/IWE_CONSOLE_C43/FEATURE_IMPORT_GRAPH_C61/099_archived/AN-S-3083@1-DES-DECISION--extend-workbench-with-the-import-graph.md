---
atom_family: SPEC
atom_id: AN-S-3083
structure:
  container:
    component: C61
  tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T10:44:30.157383+00:00'
---

## Summary

Extend Workbench with the Import Graph

## Claim

### Prose Claim

The Import Graph is a source-backed projection of the selected Project.
It inventories executable source and extracts static imports without running that source.
Record each import once with its source Module, written target, and file location.
Resolve the target as a Module or Package when the available evidence supports it.

Reuse the Workbench index for the initial scan and `SourceWatcher` for updates.
Parse changed files and resolve affected imports again when targets change.
Publish each update in one transaction in the Workbench DuckDB store.
If an update fails, write an explicit error to stderr and make no partial publication.

Extend the existing `anechoic` property graph with the import relations.
Expose Module → Module, Module → Package, Package → Module, and Package → Package.
Use Module ownership to derive Package edges and preserve direct Package imports.
Workbench and terminal SQL queries use the same graph and can trace each edge to its import.

---
atom_family: SPEC
atom_id: AN-S-3083
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: archived
  version: 6
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---

## Summary

Extend Workbench with the Import Graph

## Claim

### Prose Claim

Call the Workbench projection the Realization Graph. Reuse Module and Package
node identities across import and test Relations. A local folder with a direct executable file has one Package
node across all languages. Skip dot folders. Record each static import with its source
Module, written target, and file location. Resolve it without running source.
Keep all four Module and Package import pairs and direct Package imports.

Derive `TESTS` from a direct `<full package folder name>__tests/` subdirectory
to its parent Package, or to the declared Component when the parent has no direct executables.
Expose `IS_TESTED_BY` as the inverse. Audit missing visibility on tested Packages.
A qualifying test folder uses a Package node of type Test Package.

Reuse the Workbench index and `SourceWatcher`. Parse changed files and
resolve affected imports again when targets change. Publish each update
in one DuckDB transaction and write failures to stderr. Extend the existing
`anechoic` property graph. Workbench and terminal SQL can trace each import
to its file and line and each test Relation to its directory.

Publish Component and Component Seed Manifest `code`, `state`, and `io` declarations in
`boundary_declarations` with their owner and exact Spec revision. Publish
`code_access_findings` for denied or unresolved Python imports. Reuse cached
imports and the accepted Structure, including when its boundary rules change.
State and I/O rows describe declarations. Their analyzers provide findings separately.

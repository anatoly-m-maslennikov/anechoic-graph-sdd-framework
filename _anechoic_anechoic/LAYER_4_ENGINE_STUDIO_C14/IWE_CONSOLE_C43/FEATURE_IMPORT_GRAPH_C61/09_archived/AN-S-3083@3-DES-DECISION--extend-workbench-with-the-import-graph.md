---
atom_family: SPEC
atom_id: AN-S-3083
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3159@1
state:
  status: archived
  version: 3
  updated_at: '2026-11-20T23:12:09.705525+00:00'
---

## Summary

Extend Workbench with the Import Graph

## Claim

### Prose Claim

Call the Workbench projection the Realization Graph. Reuse Module and Package
node identities across import and test Relations. Each local folder with an executable file in its subtree has one Package
node across all languages. Skip dot folders. Record each static import with its source
Module, written target, and file location. Resolve it without running source.
Keep all four Module and Package import pairs and direct Package imports.

Derive `TESTS` from a direct `<full package folder name>__tests/` subdirectory
to its parent Package. Expose the inverse as `IS_TESTED_BY`. A qualifying test folder
uses a Package node of type Test Package. Derive these Relations for Packages
in the selected source scope, including those without a Spec or Spec Binding.

Reuse the Workbench index and `SourceWatcher`. Parse changed files and
resolve affected imports again when targets change. Publish each update
in one DuckDB transaction and write failures to stderr. Extend the existing
`anechoic` property graph. Workbench and terminal SQL can trace each import
to its file and line and each test Relation to its directory.

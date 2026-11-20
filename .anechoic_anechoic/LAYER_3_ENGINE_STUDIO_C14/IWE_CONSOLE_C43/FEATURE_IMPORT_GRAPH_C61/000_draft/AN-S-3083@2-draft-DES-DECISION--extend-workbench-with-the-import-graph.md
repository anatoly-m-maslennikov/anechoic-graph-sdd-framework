---
identity:
  atom_id: AN-S-3083
context:
  container:
    component: C61
  tier: 1
  lens: DES
  template: DECISION
state:
  status: "draft"
  version: 2
  updated_at: "2026-11-20T14:50:57.651086+00:00"
---

## Summary

Extend Workbench with the Import Graph

## Claim

### Prose Claim

Call the Workbench projection the Realization Graph. Reuse Module and Package
node identities across import and test Relations. Record each static import
with its source Module, written target, and file location. Resolve from
available evidence without running Project source. Keep all four Module and
Package import pairs, including derived Package edges and direct Package imports.

Derive `TESTS` from a direct `<full package folder name>__tests/` subdirectory
to its parent Package. Expose the inverse as `IS_TESTED_BY`. The directory
uses a Package node of type Test Package. Derive these Relations for Packages
in the selected source scope, including those without a Spec or Spec Binding.

Reuse the Workbench index and `SourceWatcher`. Parse changed files and
resolve affected imports again when targets change. Publish each update
in one DuckDB transaction and write failures to stderr. Extend the existing
`anechoic` property graph. Workbench and terminal SQL can trace each import
to its file and line and each test Relation to its directory.

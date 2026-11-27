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
  version: 7
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---

## Summary

Extend Workbench with the Import Graph

## Claim

### Prose Claim

Call the Workbench projection the Realization Graph. Reuse Module and Package
node identities across import and test Relations. Identify local Packages under
AN-S-3159 and AN-S-4837. Skip dot folders. Record each static import with its
source Module, written target, and file location. Resolve it without running
source. Keep all four Module and Package import pairs and direct Package imports.

Use AN-S-3014 and AN-S-3159 to derive Test Package Relations. Publish the
admitted Package and Component targets. Audit visibility on tested Packages.

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

---
atom_family: TKT
atom_id: AN-T-373
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: canceled
  version: 3
  updated_at: 2026-10-24 06:26:31 +0400
---
## Summary

Complete governance self-application

# Complete governance self-application

1. Backfill every existing Atom with frontmatter `version` and `updated_at` values while preserving stable filenames; complete when every Atom conforms to the applicable GOVERNANCE authority.
2. Update Atom creation and mutation mechanisms to write `version` and `updated_at` and to increment them under the applicable GOVERNANCE authority; complete when newly created and revised Atoms conform without manual repair.
3. Rebuild every existing Projection with `updated_at` through the journal-backed rebuild flow; complete when every Projection conforms to the applicable GOVERNANCE authority and every rebuild is recorded under the applicable SEMANTICS and GOVERNANCE authority.
4. Preserve existing `technical_decision` Method Atoms until the operator activates their deferred migration, then migrate them to the current Method subtype model without changing accepted meaning.
5. Implement proof-currentness derivation and generate its Catalog; complete when governed proof dependency frontiers deterministically produce `current`, `stale`, or `unknown` results under the applicable GOVERNANCE authority.

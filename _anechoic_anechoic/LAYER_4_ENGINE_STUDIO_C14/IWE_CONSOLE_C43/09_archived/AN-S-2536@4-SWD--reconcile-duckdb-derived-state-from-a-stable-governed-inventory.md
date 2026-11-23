---
atom_family: SPEC
atom_id: AN-S-2536
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 4
  updated_at: 2026-11-04 07:39:08 +0400
---

## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim scope

Technical background indexing of the selected source inventory into the in-memory DuckDB Projection.

## Claim

### Prose Claim

Technical background indexing must reconcile Current and Draft Atom carriers, excluding Archived carriers, into the in-memory DuckDB Projection. Every Current status remains included. It does not prescribe a fingerprint algorithm or a separate event-classification process.

Refresh the existing in-memory database and graph directly under the shared database-owner lock and finish a successful native write transaction with COMMIT. Queries do not run during refresh. If indexing or graph refresh fails, report the error to stderr and stop serving that failed state; do not return partial success, retry the batch, swap candidate databases, restore an old state, or perform application rollback.

An invalid, unreadable, or unstable source capture is excluded with its source-owned Projection rows and all Relation facts and graph mappings supported by it, including derived counterparts carried in other object rows. Refresh those affected rows and hashes, report the source to stderr, and skip it while valid sources continue. It is not treated as deletion, retained as stale data, or automatically resubmitted. A later actual source change is new input.

A failed indexing transaction reports its error to stderr. The failed owner requires an explicit restart rather than an automatic rollback or recovery procedure.

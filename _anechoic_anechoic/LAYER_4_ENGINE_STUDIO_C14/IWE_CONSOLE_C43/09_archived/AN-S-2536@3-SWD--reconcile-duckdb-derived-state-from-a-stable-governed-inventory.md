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
  version: 3
  updated_at: 2026-11-04 05:16:33 +0400
---

## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim scope

Technical background indexing of the selected source inventory into the in-memory DuckDB Projection.

## Claim

### Prose Claim

Technical background indexing must reconcile Current and Draft Atom carriers, excluding Archived carriers, into the in-memory DuckDB Projection. Every Current status remains included. It does not prescribe a fingerprint algorithm or a separate event-classification process.

Each indexing batch must publish one complete affected state of source rows, outgoing materialized Relations, row hashes, and the DuckPGQ graph, or publish none of that batch. Queries remain serialized with indexing until graph refresh finishes, so no public query observes old graph mappings with new table rows or a half-batch state. If graph refresh fails, report the failure and do not serve a mismatched graph as current.

An invalid, unreadable, or unstable source capture is excluded with its source-owned Projection rows and all Relation facts and graph mappings supported by it, including derived counterparts carried in other object rows. Refresh those affected rows and hashes, report the source to stderr, and skip it while valid sources continue. It is not treated as deletion, retained as stale data, or automatically resubmitted. A later actual source change is new input.

A failed indexing transaction remains uncommitted, reports the technical failure to stderr, and exposes neither a partial state nor a successful result.

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
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---

## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim scope

Technical background indexing of the selected source inventory into the in-memory DuckDB Projection.

## Claim

### Prose Claim

Technical background indexing must reconcile Current and Draft Atom carriers, excluding Archived carriers, into the in-memory DuckDB Projection. Every Current status remains included. It does not prescribe a fingerprint algorithm or a separate event-classification process.

Each indexing transaction must apply one complete affected batch of source rows and materialized derived-relation rows, or apply none of that batch. Public queries therefore observe no half-batch state.

An invalid, unreadable, or unstable source capture is excluded with its owned Projection rows, reported to stderr, and skipped while valid sources continue. It is not treated as deletion, retained as stale data, or automatically resubmitted. A later actual source change is new input.

A failed indexing transaction remains uncommitted, reports the technical failure to stderr, and exposes neither a partial state nor a successful result.

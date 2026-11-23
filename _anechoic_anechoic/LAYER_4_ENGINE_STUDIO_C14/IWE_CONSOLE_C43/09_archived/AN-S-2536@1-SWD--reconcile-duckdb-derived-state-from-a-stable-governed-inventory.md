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
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---

## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim scope

Synchronization of the DuckDB Projection with governed Atom carriers.

## Claim

### Prose Claim

The DuckDB Projection must reconcile its derived state from the complete governed source inventory on startup and periodically while the server runs. Correctness must not depend on filesystem notifications.

Reconciliation must compare source locators and content fingerprints, and it must use stable captured reads. An invalid, unreadable, or changed-during-capture source is excluded with its owned derived rows, reported to stderr, and skipped while valid sources continue. A capture set must not publish mixed source reads or automatically resubmit the same failed input. A later actual file edit, move, or new observed source state is a new input.

For each source, one database transaction must apply or remove its delivered Projection records and nested values together. Queries therefore observe one committed Projection state.

The derived state must reconcile creates, edits, renames, moves, and confirmed deletions. A move changes the source locator; it does not itself create a source Version. A source-file error does not prove deletion.

A failed database transaction must remain uncommitted, report failure through stderr and to its caller, and expose neither a partial state nor a successful result. It does not automatically start another transaction.

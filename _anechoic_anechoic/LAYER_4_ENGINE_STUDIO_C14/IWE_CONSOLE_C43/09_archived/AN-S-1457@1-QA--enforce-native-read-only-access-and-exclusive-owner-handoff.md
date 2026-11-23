---
atom_family: SPEC
atom_id: AN-S-1457
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Enforce native read-only access and exclusive owner handoff

## Claim scope

The DuckDB connection boundary between trusted synchronization and public query
access, including replacement of the long-lived owner.

## Claim

### Prose Claim

The access boundary passes when public SQL uses a native DuckDB read-only
connection and the trusted read-write owner is fully closed before any mode
handoff. Direct writes and data-modifying statements nested inside a `WITH`
query fail through the database's native mode and leave source and Projection
state unchanged. Unrelated file or network reads fail, and SQL cannot turn
external access back on after it has been disabled and configuration is locked.
A pending synchronization update waits until the query finishes; read-only and
read-write handles for the same database never overlap. A hot replacement closes
the prior owner before its successor opens, and a failed query does not prevent a
later valid synchronization update.

## Details

### Fixtures and expected outcomes

| Fixture | Expected outcome |
| --- | --- |
| Valid read-only `SELECT` | The query succeeds with no database or source mutation. |
| `INSERT`, `UPDATE`, `DELETE`, or a data-modifying CTE | The native read-only connection returns an error; no partial write is visible. |
| File or network table-function/read request | The request fails as unrelated external access; it does not read outside the Projection. |
| SQL that attempts to enable external access or flip a locked configuration | The configuration change is rejected and external access remains disabled. |
| A query that remains active while a synchronization update is pending | The update does not open a read-write handle until the query ends; no overlapping read-only/read-write ownership occurs. |
| Hot replacement of the server owner | The old owner is closed before the replacement opens, so two independent writers never own the database. |
| A failed query followed by a valid synchronization update | The failure is returned to the query caller and the synchronizer can commit its next valid update. |

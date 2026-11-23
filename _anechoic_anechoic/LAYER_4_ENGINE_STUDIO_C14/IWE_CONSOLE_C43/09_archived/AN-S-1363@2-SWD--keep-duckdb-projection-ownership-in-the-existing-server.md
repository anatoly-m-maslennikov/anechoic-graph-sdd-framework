---
atom_family: SPEC
atom_id: AN-S-1363
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

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The in-memory DuckDB Projection for one Project.

## Claim

### Prose Claim

The in-memory DuckDB Projection for one Project must have one owner in the existing server. The owner holds the Projection only in memory, creates no temporary spill files, and does not create a database server, watcher service, queue, planner, scheduler, or orchestrator.

The owner serializes technical background indexing and public native-SQL access. Query Run and Check execute synchronously in the originating MCP or web request through that owner; they are not background query work.

The Projection is rebuilt when the application restarts after code changes. This MVP does not prescribe a live implementation-generation handoff.

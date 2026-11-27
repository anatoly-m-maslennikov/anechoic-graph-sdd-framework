---
atom_family: SPEC
atom_id: AN-S-1363
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 11
  updated_at: '2026-11-14T00:32:52.424781+00:00'
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim

### Prose Claim

One serialized DuckDB owner in the existing application owns a Project’s
derived Projection and query results.

## Details

- Use the delivered database and spill locations.
- Refresh, Run, Page, and Check share the synchronous owner.
- The existing owner uses one cache and adds no database server, queue,
  planner, scheduler, or worker.

### Query results

- Each Run materializes once. Page reads use that result after source
  refresh as well. Execution and delivery have separate failure boundaries.
- The startup TTL keeps a result while young or pinned by its open View.
  Use a monotonic clock. Closing unpins the result and keeps young results.
  - This uses no heartbeat, cross-process lease, or crash recovery.
- Editing View SQL preserves the last result. An admitted rerun releases it
  before execution, even if SQL fails.
- Startup rebuild clears old results and IDs.
- First-page conversion failure removes the unrevealed result. Later
  conversion or export failure preserves the known ID and reports the error.

### Incremental refresh

- Keep parsed rows and signatures. Remove cached data for deleted, excluded,
  or invalid sources. Treat a later actual change as new input.
- Configuration staging and discarded-state restoration are outside this method.

---
atom_family: SPEC
atom_id: AN-S-2976
structure:
  container:
    component: C45
  tier: 6
context:
  lens: QA
state:
  status: draft
  version: 1
  updated_at: '2026-11-14T01:09:01.591353+00:00'
---
## Summary

Verify watcher change-log parity and query visibility

## Claim

### Prose Claim

Verify watcher event parity, bounded retention, failure handling, graph
isolation, and timed query visibility on a real Docker bind mount.

## Details

### Real operations and store parity

Use a real Docker bind-mounted temporary repository and the existing `watchdog`
Observer limited to the selected repository `control_root`. Perform actual
creation, edit, rename, move, directory, and boundary operations.

Wait through the owner loop and verify matching callback paths, file rows, and
table rows.

- Verify NDJSON and DuckDB `change_log` retain the same technical rows.
- Native add, modify, and delete produce `create`, `update`, and `remove`.
- A same-parent move is `rename`; a parent-changing move is `move`.
- Boundary entry and exit are `create` and `remove`.
- Directory create, move, and remove are recorded and indexed.
  directory-modification noise and outside-root changes are not.
- Add and delete without a native move callback remain two observations; never
  infer rename or move.
- Preserve every grouped observation without Workflow or Journal invention.

### Retention and failure boundaries

The existing owner loop performs same-thread idle cleanup. Rows expire after 48
hours, and oldest rows are removed from both stores at 100,000 rows. Restart and
full reread rehydrate live rows under the same limits.

Failed source or log write follows the existing error boundary, without an error
event row, Journal, watcher service, scheduler, retry, or recovery.

### Graph isolation

Prove `change_log` is not an `atoms` or `scope_units` source, graph vertex, or
Relation fact. It exposes only `observed_at`, `operation`, `old_path`, and
`new_path`.

### Query visibility and deadlines

Seed a deterministic valid 5,000-Atom inventory and use it for E2E mutations and
visibility timing. A result is visible only with exact ID, version, path,
Header.Container, and required direct and derived facts.

Event-log visibility or counts alone do not pass.

Report structured fixture, image, operation, count, and elapsed metrics from
mutation to query-visible result, with 500-file throughput as 500/elapsed.
Distinguish fixture and repository timing and preserve correctness deadlines.

- Ordinary mutation: at most 1.5 seconds.
- 500 add, update, or delete operations: at most 15 seconds.
- 500 moves or filename renames, including required carrier metadata: at most 30
  seconds.
- Combined rename plus Header/content update: at most 30 seconds.

Observation timeout is separate. No variable may raise or disable the limits.

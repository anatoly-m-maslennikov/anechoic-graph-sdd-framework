---
atom_family: SPEC
atom_id: AN-S-2536
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 27
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim

### Prose Claim

Index Current and Draft Atom carriers, excluding Archived carriers, into the file-backed Projection; all Current statuses remain included. A role-only unnumbered Draft reference is technically unique only as marker plus Project-relative carrier path; do not change that ID or weaken numbered Current/Draft identity.

Use the existing server's `watchdog` Observer and selected-repository watcher owner, observing only `control_root`, with grouped native callbacks. Preserve initial build, retained-log reread at owner start/full reread, idle 48-hour cleanup on the same owner thread and Observer shutdown. Under the owner lock, persist events before refresh. Normal batches append/INSERT additions only, retain equal duplicates, and never rewrite retained rows except owner-start/full-reread reconciliation or TTL/cap cleanup. Record directory create/move/remove and refresh the index; ignore directory-modification noise and outside paths, and never infer move from add/delete. A mounted parent does not enlarge the boundary; do not add a watcher service, scheduler, retry or recovery, or failure-as-event-row.

Refresh database and graph under the shared owner lock in one native COMMIT transaction. Queries do not run during refresh. Failed indexing/graph refresh reports stderr and leaves the owner unavailable pending explicit restart: no partial state, candidate swap, rollback or recovery. Invalid ordinary capture is excluded with its supported rows/facts and later actual change is new input; ambiguous references, relation keys or inverse metadata warn and omit only the affected facts. An invalid Current Scope Unit Declaration stops indexing rather than being skipped. A resource-limit kill is a runtime/capacity failure, not invalid-source evidence.

Retain parsed rows, signatures and owner-local deltas. Ordinary events update only changed public rows, affected inverse neighbours, mappings and hashes in one transaction; unchanged rows preserve object identity and values. Initial indexing, explicit full reread and actual structural/relation-registry/schema changes may rebuild the affected projection, never generic recovery. Publish state only after the database update succeeds. Preserve referenced endpoint contributions until no node or edge supports them; deletion, rename, invalidation, repair and target reappearance must not duplicate facts.

Emit post-COMMIT INFO metrics (operation, table, count/reference, monotonic elapsed and refresh phases) without changing stderr diagnostics or creating Journal events. Case-colliding native relation labels warn and omit colliding projected links while raw source facts remain. Preserve UTF-8 original Markdown and reconstruct heading text transiently; do not retain duplicate decoded bodies or second per-source Header maps.

## Details

### Claim scope

Technical background indexing of the selected source inventory into the file-backed DuckDB Projection.

### Direct indexing inputs and publication

Read YAML and actual Markdown headings directly, using generated declaration assets where admitted. Keep indexed source rows, `atoms`/`scope_units`, relation materialization, hashes and graph publication consistent with the successful transaction; `change_log` is technical observation data, not a source or graph fact.

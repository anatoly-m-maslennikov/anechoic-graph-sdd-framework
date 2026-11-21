---
atom_family: SPEC
atom_id: AN-S-2536
structure:
  container:
    component: C45
  tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 31
  updated_at: '2026-11-13T19:29:08.684198+00:00'
---
## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim

### Prose Claim

Index Current, Draft and Backlog carriers into the file-backed Projection at startup. Resolve explicit Archive load requests through the Scope Unit and Role placement rules. Keep a lightweight Archive filename inventory for lifecycle identity and Version reservations, and parse Archive contents only for selected folders or exact lifecycle files. Update files in the loaded Archive scope on source changes. A role-only unnumbered Draft reference is technically unique only as marker plus Project-relative carrier path. Preserve that ID and numbered Current/Draft identity.

Use the existing server's `watchdog` Observer with grouped native callbacks. Watch the Project control root for Atom changes and the Workbench implementation root for Spec Trace changes. Record only control-root events in `change_log`. Preserve initial build, retained-log reread at owner start/full reread, idle 48-hour cleanup on the same owner thread and Observer shutdown. Under the owner lock, persist events before refresh. Normal batches append/INSERT additions only, retain equal duplicates, and never rewrite retained rows except owner-start/full-reread reconciliation or TTL/cap cleanup. Record directory create/move/remove and refresh the index; ignore directory-modification noise and outside paths, and never infer move from add/delete. A mounted parent does not enlarge the boundary; do not add a watcher service, scheduler, retry or recovery, or failure-as-event-row.

Refresh database and graph under the shared owner lock in one native COMMIT transaction. Queries do not run during refresh. Failed indexing/graph refresh reports stderr and leaves the owner unavailable pending explicit restart: no partial state, candidate swap, rollback or recovery. Unreadable or unparseable ordinary capture is excluded with its supported rows and facts. Keep parseable source rows and report current-schema violations separately. Later actual change is new input. Ambiguous references, relation keys or inverse metadata warn and omit only the affected facts. An invalid Current Scope Unit Declaration stops indexing rather than being skipped. A resource-limit kill is a runtime/capacity failure, not invalid-source evidence.

Retain parsed rows, signatures and owner-local deltas. Ordinary events update only changed public rows, affected inverse neighbours, mappings and hashes in one transaction; unchanged rows preserve object identity and values. Do not traverse or copy the full inventory for an ordinary Atom delta. Initial indexing, explicit full reread and Current structural source changes may rebuild the affected data projection under the installed schema and registry. Rebuild the image to change those compiled assets. For independent Archive and Promote Draft batch targets, group the paths changed by completed writes into one DuckDB refresh. Keep target order, failure and effects per target. If a later target needs an earlier target’s published result or the grouped path is inapplicable, use individual refreshes. Publish state only after the database update succeeds. Preserve referenced endpoint contributions until no node or edge supports them; deletion, rename, invalidation, repair and target reappearance must not duplicate facts.

Emit post-COMMIT INFO metrics (operation, table, count/reference, monotonic elapsed and refresh phases) without changing stderr diagnostics or creating Journal events. Case-colliding native relation labels warn and omit colliding projected links while raw source facts remain. Preserve UTF-8 original Markdown and reconstruct heading text transiently; do not retain duplicate decoded bodies or second per-source Header maps.

## Details

### Claim scope

Technical background indexing of the selected source inventory into the file-backed DuckDB Projection.

### Direct indexing inputs and publication

Read YAML and actual Markdown headings directly, using generated declaration assets where admitted. Keep indexed source rows, `atoms`/`scope_units`, relation materialization, hashes and graph publication consistent with the successful transaction. Submit audit work after publishing the source data. `change_log` is technical observation data.

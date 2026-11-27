---
atom_family: SPEC
atom_id: AN-S-2536
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 36
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Reconcile DuckDB derived state from a stable governed inventory.

## Claim

### Prose Claim

Index native Current, Draft and Backlog carriers into the file-backed Projection at startup. Legacy Workbench resolves explicit Archive load requests through Scope Unit and Role placement rules. It keeps a lightweight Archive filename inventory for lifecycle identity and Version reservations, parses Archive contents only for selected folders or exact lifecycle files, and updates files in loaded Archive scope on source changes. Its role-only unnumbered Draft reference is technically unique only as marker plus Project-relative carrier path. Preserve that ID and numbered Current/Draft identity.

Use the existing server's `watchdog` Observer with grouped native callbacks. Watch the Project control root for Atom changes and the Workbench implementation root for Spec Trace changes. Apply AN-S-1352 to `change_log`. Preserve the initial build, idle 48-hour cleanup on the owner thread, and Observer shutdown. Persist events before refresh under the owner lock. Normal batches append or INSERT additions only. Rewrite retained rows during owner-start or full-reread reconciliation or TTL or cap cleanup. A mounted parent does not enlarge the boundary. Add no watcher service, scheduler, retry, recovery, or failure-as-event row.

Refresh database and graph under the shared owner lock in one native COMMIT transaction. Queries do not run during refresh. Failed indexing/graph refresh reports stderr and leaves the owner unavailable until an explicit restart. Roll back failed SQL writes. Add no candidate swap or application recovery. Unreadable or unparseable ordinary capture is excluded with its supported rows and facts. Keep parseable source rows and report current-schema violations separately. Later actual change is new input. Ambiguous references, relation keys or inverse metadata warn and omit only the affected facts. In legacy Workbench, an invalid Current Scope Unit Declaration stops indexing rather than being skipped. A resource-limit kill is a runtime/capacity failure, not invalid-source evidence.

Retain parsed rows, signatures and owner-local deltas. Ordinary events update only changed public rows, affected inverse neighbours, mappings and hashes in one transaction; unchanged rows preserve object identity and values. Do not traverse or copy the full inventory for an ordinary Atom delta. Initial indexing, explicit full reread and Current structural source changes may rebuild the affected data projection under the installed schema and registry. Rebuild the image to change those compiled assets. Apply AN-S-2529 to group completed Archive and Promote Draft writes. Keep target order, failure and effects per target. If a later target needs an earlier target’s published result or the grouped path is inapplicable, use individual refreshes. Publish state only after the database update succeeds. Preserve referenced endpoint contributions until no node or edge supports them; deletion, rename, invalidation, repair and target reappearance must not duplicate facts.

Emit post-COMMIT INFO metrics (operation, table, count/reference, monotonic elapsed and refresh phases) without changing stderr diagnostics or creating Journal events. Case-colliding native relation labels warn and omit colliding projected links while raw source facts remain. Preserve UTF-8 original Markdown and reconstruct heading text transiently; do not retain duplicate decoded bodies or second per-source Header maps.

## Details

### Claim scope

Technical background indexing of the selected source inventory into the file-backed DuckDB Projection.

### Direct indexing inputs and publication

Read YAML and actual Markdown headings directly, using generated declaration assets where admitted. Keep indexed source rows, `atoms`/`scope_units`, relation materialization, hashes and graph publication consistent with the successful transaction. Apply AN-S-1948 and AN-S-1967 to audit publication. Rebuild available audit tables from their current providers. `change_log` is technical observation data.

### Native startup and on-demand rebuild

Apply AN-S-3116 at startup, AN-S-3156 to the rebuild, and AN-S-1363
to retained results. Validate the target before writing. Report the
failing target to stderr and in the HTTP or MCP error response. Require
an explicit restart if failure may have invalidated the graph.

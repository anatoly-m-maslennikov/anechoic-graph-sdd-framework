---
atom_family: SPEC
atom_id: AN-S-1363
container:
  component: C45
tier: 4
context:
  lens: SWD
relations:
  IS_REFERENCE:
  - AN-S-3116@1
state:
  status: active
  version: 14
  updated_at: "2026-11-24T14:50:25.261863+00:00"
---
## Summary

Keep DuckDB Projection ownership in the existing server.

## Claim scope

The derived DuckDB Projection and query results for one Project.

## Claim

### Prose Claim

- Give one Kernel process ownership of the Project database and spill paths.
- A second writer process exits with an explicit lock error.
- Serialize refresh, Run, Page, and Check inside the Kernel.
- Keep parsed-source rows and signatures for incremental refresh.
- Remove cached parse data for deleted, excluded, or invalid sources.
- Treat later source changes as new input.
- Add no configuration staging, second cache, or discarded-state restoration.

- Materialize each Run once in a result table in the configured Workbench database.
- Page reads the snapshot, including after an ordinary source refresh.
- Keep execution and delivery failures separate.
- Measure the startup TTL with a monotonic clock.
- Keep a result while it is young, pinned by its View, or needed by a live result.
- Keep source snapshots through every level of a live result's dependencies.
- Closing a View unpins its snapshot. The normal retention rules still apply.
- Add no heartbeat, cross-process lease, or crash recovery.
- Keep the snapshot when the Operator edits View SQL.
- Release the prior result ID when a valid rerun starts, even if execution fails.
- Clear result tables, IDs, and View bindings at startup.
- Remove an unrevealed result if first-page conversion fails.
- Report later conversion or export errors. Keep the known result ID.

- Rebuild affected live snapshots from the last executed SQL and effective options.
- Use current inputs when rebuilding one result table or all tables.
- Rebuild source snapshots before their dependents.
- Publish replacement IDs, View bindings, and pins together.
- Preserve unsynced View SQL when its snapshot changes.
- Return the old-to-new ID map to the caller.
- Repeat neither save nor export during a rebuild.

### Formal Claim

The model checks one dependency edge in a successful full rebuild. Every materialization of the dependent requires a fresh upstream binding.

```lean
namespace SavedQueryRebuild

inductive Effect where
  | materialize (query : Nat)
  | drop (query : Nat)
  | bind (query : Nat)

def scan (upstream dependent : Nat) : List Effect → Bool → Bool
  | [], _ => true
  | .materialize query :: rest, fresh =>
      (query != dependent || fresh) && scan upstream dependent rest fresh
  | .drop query :: rest, fresh =>
      scan upstream dependent rest (if query == upstream then false else fresh)
  | .bind query :: rest, fresh =>
      scan upstream dependent rest (if query == upstream then true else fresh)

def readsFresh (effects : List Effect) (upstream dependent : Nat) : Bool :=
  scan upstream dependent effects false

end SavedQueryRebuild
```

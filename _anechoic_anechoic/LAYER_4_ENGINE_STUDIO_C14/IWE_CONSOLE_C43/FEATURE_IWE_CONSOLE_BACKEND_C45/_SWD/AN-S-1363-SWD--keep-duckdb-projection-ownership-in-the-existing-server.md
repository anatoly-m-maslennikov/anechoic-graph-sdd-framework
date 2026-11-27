---
atom_family: SPEC
atom_id: AN-S-1363
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
  version: 16
  updated_at: "2026-11-27T17:35:01.150345+00:00"
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
- Apply AN-S-2536 to retained parse rows, signatures, and incremental refresh.
- Remove cached parse data for deleted, excluded, or invalid sources.
- Treat later source changes as new input.
- Add no configuration staging, second cache, or discarded-state restoration.

- Apply AN-S-5170 to materialization, retention, and release of query results.

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

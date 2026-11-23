---
atom_family: SPEC
atom_id: AN-S-2535
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

Preserve governed Atom data and reuse native SQL.

## Claim scope

In-memory reading, schema Projection, and query semantics for Current and Draft Atom carriers excluding Archived carriers.

## Claim

### Prose Claim

The DuckDB Projection reader must read Current and Draft Atom carriers, excluding Archived carriers, into memory. Every Current status, including Done and Canceled, remains in that inventory. It parses YAML and Markdown according to in-memory schema Projections of the relevant current model Declarations. It must not use a generic CFEL evaluator or a prose interpreter.

The in-memory schema Projections identify admitted Header and Content Properties, their Markdown structure, and declared Relation Types. They remain in memory and do not create JSON files or a third public database table. Parent paths are derived from Property paths.

Only Current Scope Unit Declarations establish the current Scope Unit inventory. A Draft Declaration remains a queryable Atom but does not establish a current Scope Unit.

Source Atoms retain direct Relations only. The Projection materializes declared derived Relations in memory and rebuilds the affected materialized rows after a source or relevant Declaration changes. Each public row hash includes its materialized Relations. Each in-memory schema Projection row uses the same `hash` rule: hash its deterministic canonical row value with `hash` excluded.

Use DuckDB as the SQL engine and reuse its native SQL behavior. The only ANECHOIC graph extension is the minimal `expand` helper over indexed registered Relation Types: it resolves an unambiguous seed, follows selected directions, includes each reachable reference once, terminates cycles, and returns references rather than embedded objects. The Projection does not add a SQL-like parser or evaluate Formal Claims.

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
  version: 3
  updated_at: 2026-11-04 05:16:33 +0400
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

Source Atoms retain direct Relations only. Each indexed object row carries that object's outgoing direct and declared-derived Relations. For `Task IS_CONTAINED_BY Epic`, the Task row carries `IS_CONTAINED_BY` and the Epic row carries the derived `CONTAINS`. A source or relevant Declaration change refreshes every affected outgoing-relation row, graph mapping, and row hash, including rows for unchanged target sources. This does not edit those sources or increment their Versions. Each public row hash includes its materialized Relations. Each in-memory schema Projection row uses the same `hash` rule: hash its deterministic canonical row value with `hash` excluded.

Use DuckDB for SQL and the DuckPGQ community extension for SQL/PGQ graph queries. Register an in-memory property graph over the indexed objects and their materialized registered Relation facts. Reuse DuckPGQ for pattern matching and traversal instead of implementing a ANECHOIC traversal engine or requiring a custom `expand()` API.

Reachability queries must still satisfy the Relation-expansion requirement: resolve an unambiguous typed seed, follow the selected Relation Types and directions, include the seed and each reachable typed reference once, and terminate on cycles. Use native SQL and SQL/PGQ to produce that result; joins or subqueries fetch the selected objects. Querying a declared inverse uses its materialized fact and does not synthesize it again. The Projection does not add a SQL-like parser, evaluate Formal Claims, or adopt graph algorithms beyond the selected query requirements.

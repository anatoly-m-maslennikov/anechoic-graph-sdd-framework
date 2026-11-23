---
atom_family: SPEC
atom_id: AN-S-1366
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Query native SQL results and typed Relation expansion

## Claim scope

Native SQL and typed relation expansion over in-memory Projection rows.

## Claim

### Prose Claim

Native DuckDB SQL returns exactly requested columns, types, counts, and complete rows. `expand` reads materialized direct and declared-derived nested relation facts, returns typed references, includes the unambiguous seed and each reachable reference once, and terminates on cycles. It neither fetches objects nor infers prose links or synthesizes a second inverse. Relation materialization stays in memory and creates no public relation table or view.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Valid selection, join, CTE, aggregation, ordering, string, and regex query | Native DuckDB returns requested columns and all rows with exact counts. |
| `SELECT COUNT(*) FROM atoms` | Only the requested aggregate appears; no `atoms.hash` is added. |
| Direct fact and declared inverse | Refreshed nested facts are materialized once each; `expand` returns no duplicate inverse traversal. |
| Cyclic selected relations | `expand` returns seed and reachable typed references once, then terminates. |
| Unregistered relation or prose/Formal Claim text | It is not materialized or traversed. |

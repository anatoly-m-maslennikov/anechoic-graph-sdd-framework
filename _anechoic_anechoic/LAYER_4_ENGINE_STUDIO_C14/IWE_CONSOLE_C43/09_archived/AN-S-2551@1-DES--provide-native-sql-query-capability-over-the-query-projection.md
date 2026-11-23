---
atom_family: SPEC
atom_id: AN-S-2551
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Provide native SQL query capability over the query Projection

## Claim scope

Queries over the synchronized Atom query Projection.

## Claim

### Prose Claim

The query capability **must**:

- keep public queries read-only; they do not change source files or the query Projection.

- accept native SQL according to the selected SQL engine's semantics, including SELECT, FROM, WHERE, CTEs, subqueries, aggregation, GROUP BY, HAVING, sorting, string functions, and regular expressions.
- expose nested Header data and nested Content Properties without flattening their source distinctions.
- use the selected SQL engine for SQL semantics rather than introduce another SQL-like parser or evaluator.
- return a query error for invalid SQL; it **must not** return an empty successful result instead.
- keep source-file errors distinct from SQL errors.


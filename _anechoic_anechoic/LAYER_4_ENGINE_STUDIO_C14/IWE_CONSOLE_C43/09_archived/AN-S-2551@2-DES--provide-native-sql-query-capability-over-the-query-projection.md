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
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Provide native SQL query capability over the query Projection

## Claim scope

Queries over the synchronized Atom query Projection.

## Claim

### Prose Claim

The query capability **must**:

- keep public queries read-only; they do not change source files or the query Projection.
- execute each public query synchronously and return its result or error to its originating MCP or web request.
- accept native SQL according to the selected SQL engine's semantics.
- expose the parsed Header and mapped Content Properties without flattening their source distinctions.
- use the selected SQL engine for SQL semantics rather than introduce another SQL-like parser or evaluator.
- return a query error for invalid SQL; it **must not** return an empty successful result instead.
- keep source-file errors distinct from SQL errors.

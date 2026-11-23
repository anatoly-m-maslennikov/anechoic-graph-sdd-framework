---
atom_family: SPEC
atom_id: AN-S-1955
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

Return complete, consistent results for query Run and Check

## Claim scope

The public Run and Check operations for a query over the query Projection.

## Claim

### Prose Claim

The query interface **must**:

- provide an MCP query tool with synchronous Run and Check operations.

- make Run return the complete query result, column names and types, row count, and column count.
- make Check return whether the query is valid and, when valid, its exact row count and column count; exact counts come from executing the read-only query.
- make the counts and rows of one Run describe the same query execution.
- return query errors to the caller through both Run and Check.
- neither silently add a LIMIT nor truncate rows. If a transport cannot carry the complete result, it **must** report that limit explicitly.
- keep Check free of source and Projection modifications.


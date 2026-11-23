---
atom_family: SPEC
atom_id: AN-S-2550
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 16:59:55 +0400
---
## Summary

Provide a simple web query interface over the shared query capability

## Claim scope

The UX of the local web interface for queries over the query Projection.

## Claim

### Prose Claim

The web interface **must**:

- provide a SQL text area and synchronous Run and Check actions.
- show ordinary result rows in navigable pages, exact total row and column counts, and query errors.
- use a small reusable component palette for consistent controls and result presentation.
- keep presentation, formatting, page navigation and UI state in the frontend; SQL filtering, sorting and aggregation remain in the database.
- use the same query capability as MCP.
- remain within the existing local application boundary.
- avoid custom TABLE, DOC, or TREE result modes.

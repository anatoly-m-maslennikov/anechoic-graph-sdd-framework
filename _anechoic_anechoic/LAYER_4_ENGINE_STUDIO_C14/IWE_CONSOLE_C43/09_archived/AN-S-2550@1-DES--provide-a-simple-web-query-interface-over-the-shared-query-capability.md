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
  version: 1
  updated_at: 2026-11-03 23:17:14 +0400
---
## Summary

Provide a simple web query interface over the shared query capability

## Claim scope

The local web interface for queries over the query Projection.

## Claim

### Prose Claim

The web interface **must**:

- provide a SQL text area and Run and Check actions.
- show ordinary result rows, row and column counts, and query errors.
- use the same query capability as the public query interface.
- remain within the existing local application boundary.
- avoid custom TABLE, DOC, or TREE result modes.


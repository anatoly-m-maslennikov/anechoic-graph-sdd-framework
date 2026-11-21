---
atom_family: SPEC
atom_id: AN-S-2530
structure:
  container:
    component: C45
  tier: 7
context:
  lens: QA
state:
  status: draft
  version: 2
  updated_at: '2026-11-13T23:56:18.808271+00:00'
---
## Summary

Verify MCP query recovery after rejected SQL

## Claim

### Prose Claim

Verify in the Workbench Docker MCP test that the same client can run valid SQL
after a rejected query.

## Details

### Rejected SQL

- Submit invalid SQL to the MCP Run tool.
- Verify that the tool reports a query failure.

### Recovery

- Run valid SQL on the same MCP client.
- Verify that it returns a successful result.

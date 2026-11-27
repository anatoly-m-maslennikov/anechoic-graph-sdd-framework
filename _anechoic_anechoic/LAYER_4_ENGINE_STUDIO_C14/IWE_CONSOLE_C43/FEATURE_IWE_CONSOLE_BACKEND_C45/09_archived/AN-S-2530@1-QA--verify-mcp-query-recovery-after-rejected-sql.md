---
atom_family: SPEC
atom_id: AN-S-2530
container:
  component: C45
tier: 7
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: '2026-11-13T19:28:04.075231+00:00'
---
## Summary

Verify MCP query recovery after rejected SQL

## Claim scope

The Workbench Docker MCP end-to-end test.

## Claim

### Prose Claim

Submit invalid SQL to the MCP Run tool and verify that it reports a query failure. Run valid SQL on the same MCP client and verify that it returns a successful result.

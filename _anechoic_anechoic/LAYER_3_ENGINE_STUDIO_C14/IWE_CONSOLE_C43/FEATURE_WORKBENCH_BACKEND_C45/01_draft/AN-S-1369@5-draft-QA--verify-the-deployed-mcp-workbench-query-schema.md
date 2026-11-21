---
atom_family: SPEC
atom_id: AN-S-1369
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-14T07:52:57.241838+00:00'
---
## Summary

Verify the deployed MCP Workbench query schema.

## Claim

### Prose Claim

Verify that deployed MCP requires `sql` and accepts a non-negative integer
`preview` and boolean `save` as optional arguments.

Use a native SDK call with `preview: 0` and `save: false`. It returns zero
preview rows, creates no saved query, and preserves the shared contract.

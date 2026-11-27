---
atom_family: SPEC
atom_id: AN-S-1369
container:
  component: C45
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 00:09:26 +0400
---

## Summary

Verify the deployed MCP Workbench query schema.

## Claim

### Prose Claim

The deployed MCP query operation advertises the shared Workbench query
contract: `sql` is required, and `preview` and `save` are accepted optional
arguments with their native types. A native MCP SDK client can send
`preview: 0` and `save: false` through the deployed endpoint without schema
rejection, while the shared query result and saved-resource behavior remain
consistent.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Deployed MCP tool schema | The advertised schema includes optional `preview` as a non-negative integer and `save` as a boolean, without rejecting either property. |
| Native SDK request with `preview: 0` and `save: false` | The request reaches the Workbench query operation and returns the expected zero-row preview without creating a saved query. |

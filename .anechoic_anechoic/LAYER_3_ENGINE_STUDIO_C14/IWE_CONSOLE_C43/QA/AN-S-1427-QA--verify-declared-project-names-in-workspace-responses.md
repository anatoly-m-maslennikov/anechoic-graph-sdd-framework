---
identity:
  atom_id: AN-S-1427
context:
  container:
    component: C43
  tier: 5
  lens: QA
state:
  status: active
  version: 1
  updated_at: 2026-11-10 21:18:04 +0400
---

## Summary

Verify declared Project names in Workspace responses

## Claim scope

Shared HTTP and MCP Workspace Open and Get responses.

## Claim

### Prose Claim

HTTP and MCP `workspace_open` and `workspace_get` must return the declared Project name, without storing that name in Workspace documents.

## Details

Use a Project whose declared name differs from its directory basename. Call Open and Get through both interfaces and check that `project_name` equals the declared name. Inspect the resulting Workspace documents and check that they contain no persisted Project-name field.

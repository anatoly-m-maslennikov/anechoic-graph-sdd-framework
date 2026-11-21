---
atom_family: SPEC
atom_id: AN-S-1427
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 2
  updated_at: '2026-11-14T07:53:00.795676+00:00'
---
## Summary

Verify declared Project names in Workspace responses

## Claim

### Prose Claim

Verify that HTTP and MCP Workspace Open and Get return the declared Project
name without persisting it in Workspace documents.

Use a Project whose declared name differs from its directory basename.
Check `project_name` in both responses and inspect the saved Workspace.

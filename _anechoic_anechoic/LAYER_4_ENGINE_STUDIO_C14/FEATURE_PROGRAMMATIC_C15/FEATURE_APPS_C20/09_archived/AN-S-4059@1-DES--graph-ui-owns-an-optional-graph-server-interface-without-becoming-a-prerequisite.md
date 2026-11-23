---
atom_family: SPEC
atom_id: AN-S-4059
container:
  component: C20
tier: 0
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 23:57:07 +0400
---
## Summary

GRAPH_UI owns an optional GRAPH_SERVER interface without becoming a prerequisite

## Claim

GRAPH_UI:

- **must** own the optional human-facing interface over GRAPH_SERVER; **and**
- **must not** become a prerequisite for headless graph access, Tools, **or** MCP.

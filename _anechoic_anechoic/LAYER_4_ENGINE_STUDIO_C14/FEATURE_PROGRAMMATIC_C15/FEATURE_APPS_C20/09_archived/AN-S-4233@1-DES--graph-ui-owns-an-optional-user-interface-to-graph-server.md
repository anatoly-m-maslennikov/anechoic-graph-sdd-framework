---
atom_family: SPEC
atom_id: AN-S-4233
container:
  component: C20
tier: 0
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-30 03:11:57 +0400
---
## Summary

GRAPH_UI owns an optional user interface to GRAPH_SERVER

## Claim

GRAPH_UI **must** own the optional human-facing interface over GRAPH_SERVER. GRAPH_UI **must not** be a prerequisite for **any** of the following:

- headless graph access;
- Tools; **or**
- MCP.

---
atom_family: SPEC
atom_id: AN-S-1914
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Bound and control MCP requests

# Bound and control MCP requests

MCP **must** validate **every** admitted protocol message **before** dispatch, apply declared time **and** resource bounds, support cancellation **without** corrupting Tool **or** project state, **and** expose progress for admitted long-running operations. Invalid, expired, cancelled, **or** resource-exhausted requests **must** terminate with explicit structured outcomes **and** **must not** leave an ungoverned background operation.

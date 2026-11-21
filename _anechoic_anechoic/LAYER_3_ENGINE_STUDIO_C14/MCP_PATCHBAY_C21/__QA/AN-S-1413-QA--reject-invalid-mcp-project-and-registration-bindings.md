---
atom_family: SPEC
atom_id: AN-S-1413
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: active
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary


Reject invalid MCP Project and registration bindings

## Claim

### Prose Claim

Verify that an MCP invocation binds to one validated ProjectSelection and current generated registration revision. Reject a foreign, missing or stale selected binding before Tool invocation.

## Details

Invoke through a foreign Project binding and a stale registration revision. Both fail before Tool execution with provenance identifying the failed boundary; no root or revision is guessed.

---
atom_family: SPEC
atom_id: AN-S-1386
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Enforce least authority and secret boundaries

## Claim

### Prose Claim

MCP **must** grant each projected capability no more authority than its source Tool requires **and** **must** preserve **all** Tool authorization **and** permission checks. Credentials **must** remain bound **to** their admitted transport **and** resource, **and** secrets **must not** appear **in** Tool discovery, model-readable results, diagnostics, logs, progress messages, **or** generated registries.

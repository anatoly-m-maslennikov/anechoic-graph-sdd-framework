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
  version: 16
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Enforce least authority and secret boundaries

# Enforce least authority and secret boundaries

MCP **must** grant each projected capability no more authority than its source Tool requires **and** **must** preserve **all** Tool authorization **and** permission checks. Credentials **must** remain bound **to** their admitted transport **and** resource, **and** secrets **must not** appear **in** Tool discovery, model-readable results, diagnostics, logs, progress messages, **or** generated registries.

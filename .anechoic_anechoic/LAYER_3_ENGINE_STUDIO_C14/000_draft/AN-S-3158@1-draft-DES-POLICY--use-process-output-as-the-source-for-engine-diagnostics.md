---
identity:
  atom_id: AN-S-3158
context:
  container:
    component: C14
  tier: 1
  lens: DES
  template: POLICY
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T15:46:41.967457+00:00'
---

## Summary

Use process output as the source for Engine diagnostics

## Claim

### Prose Claim

Use process output as the single source of truth for Engine diagnostics at
ERROR, WARNING, INFO, and DEBUG levels. Use the existing diagnostic path.
Keep the configured severity, redaction, and DEBUG limits.

Write each request error to the process stream and return it in the HTTP
or MCP response. Background components report failures through the same
process output. When stdout carries MCP messages, send diagnostics to stderr.
Derive diagnostic views from these events. Keep business Journal Records
under their existing authority.

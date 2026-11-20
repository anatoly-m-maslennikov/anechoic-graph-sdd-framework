---
atom_family: SPEC
atom_id: AN-S-3158
structure:
  container:
    component: C14
  tier: 1
context:
  template: POLICY
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T16:02:36.462788+00:00'
---

## Summary

Use process output as the source for Engine diagnostics

## Claim

### Prose Claim

- Use process output as the single source of truth for Engine diagnostics.
- Use the existing diagnostic path for ERROR, WARNING, INFO, and DEBUG.
- Keep the configured severity, redaction, and DEBUG limits.
- Log HTTP and MCP request errors to stderr. Return them in the response.
- Report background failures, including SAM daemon and FileWatcher failures, to stderr.
- Send diagnostics to stderr when stdout carries MCP messages.
- Derive diagnostic views from the process events.
- Keep business Journal Records under their existing authority.

---
atom_family: SPEC
atom_id: AN-S-3730
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify MCP reload publication and rollback

## Claim

### Prose Claim

the MCP Evaluation **must** verify implementation reload through the real stdio protocol with controlled mock implementations.

## Details

### Reload publication checks

- Keep one client connection open; call A, reload B, then call B without reconnect. Add/remove/change a Tool contract and verify published list plus negotiated notification.
- Submit syntax-invalid code, initialization failure, duplicate Tool names, or invalid schemas; verify rejection and continued service from A. Reload the same frontier twice and verify unchanged generation/no duplicate effects.
- Submit an extra field, traversal path, or alternate Project root; verify rejection before execution. Distinguish sent notification from unconfirmed client refresh; mocks do not prove Codex desktop discovery.
- With hot reload disabled by default, MCP and Workbench retain tools without an implementation child and code changes require normal restart. With explicit opt-in, run existing reload publication/failure checks.

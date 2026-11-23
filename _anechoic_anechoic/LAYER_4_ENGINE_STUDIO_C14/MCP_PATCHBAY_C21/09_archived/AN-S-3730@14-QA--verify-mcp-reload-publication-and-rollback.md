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
  version: 14
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify MCP reload publication and rollback

## Claim

### Prose Claim

the MCP Evaluation **must** verify implementation reload through the real stdio protocol with controlled mock implementations.

## Details

### Scope

server-side hot reload for the Project-local MCP gateway.

- keep one client connection open; call implementation A, reload B, then call B successfully without reconnect.
- add, remove **and** change a Tool contract; verify the published list **and** negotiated notification.
- submit syntax-invalid code, initialization failure, duplicate Tool names **and** invalid schemas; verify rejection **and** continued service from A.
- reload the same frontier twice; verify unchanged generation **and** no duplicate effects.
- submit an extra field, traversal path **or** alternate Project root; verify rejection before execution.
- distinguish sent notification from unconfirmed client refresh; mocks do **not** prove Codex desktop discovery.



With hot reload disabled by default, verify that MCP and Workbench serve their retained tools without starting an implementation child; code changes require normal process restart. With explicit opt-in, run the existing reload publication/failure checks.

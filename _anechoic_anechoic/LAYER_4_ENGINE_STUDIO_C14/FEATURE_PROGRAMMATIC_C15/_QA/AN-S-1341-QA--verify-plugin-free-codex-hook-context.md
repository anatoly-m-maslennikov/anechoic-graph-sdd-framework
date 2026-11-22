---
atom_family: SPEC
atom_id: AN-S-1341
container:
  component: C15
tier: 6
context:
  lens: QA
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify plugin-free Codex hook context

## Claim

### Prose Claim

With no Workbench plugin installed, send a native Codex hook event containing a Project binding, session ID and ANECHOIC Tool arguments. Verify that the public MCP schema accepts the added outer context, the hook reads `event.session_id` as `codex_session_id`, sends its unchanged value as `caller_context.session_id`, and the adapter passes it as generic runtime context `session_id`, and native Tool arguments remain unchanged.

Include a Tool with its own `session_id` argument. Verify that this native argument survives unchanged and is separate from runtime context `session_id`. Check that the backend accepts generic session context without a Codex-specific field or plugin. Check absent, invalid and conflicting context, an unrelated Tool call, and a stateless call without a session. Context errors must not select a fallback Project or session.

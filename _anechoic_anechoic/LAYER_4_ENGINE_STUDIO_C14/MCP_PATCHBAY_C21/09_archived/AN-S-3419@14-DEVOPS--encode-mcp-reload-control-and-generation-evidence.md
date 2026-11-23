---
atom_family: SPEC
atom_id: AN-S-3419
container:
  component: C21
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 14
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Encode MCP reload control and generation evidence

## Claim

### Prose Claim

the MCP gateway **must** carry reload requests **and** generation evidence through the following explicit interfaces.

## Details

### Scope and controls

Server-side hot reload for the Project-local MCP gateway is available only with explicit ANECHOIC_HOT_RELOAD=1; absent/other values keep it disabled. Default startup is one MCP process, omits reload-only controls, and applies code changes only after process/container restart. Forward the switch explicitly through Docker service environments.

- Keep implementation under LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_MCP, with the existing --project-root binding and stdio transport.
- reload_mcp_implementation accepts only operation reload and caller-chosen request_id; annotations are read_only_hint=false, destructive_hint=false, idempotent_hint=true, open_world_hint=false.
- get_mcp_reload_status accepts an empty request with read-only/idempotent/non-destructive/non-open-world annotations; it reads generation state without preparing, publishing, or persisting a reload.
- Reject arbitrary filesystem paths, shell commands, and alternate Project roots. Annotations describe behavior and do not override client permission policy.
- Evidence carries request/previous/active generation, implementation/registry fingerprints, registry change, notification status, client-refresh status, and diagnostics. Outcomes are reloaded, unchanged, rejected, or failed; status reports generation and in-flight counts without initiating reload. Notification status distinguishes sent/unsupported/failed; client refresh defaults unconfirmed.
- Store operational receipts under .anechoic_install/mcp_hot_reload/; they are execution evidence, not Atom authority. Use the declared Project runtime; do not install packages implicitly. Reload registered implementations, not gateway code or protocol runtime; gateway changes require reconnect.

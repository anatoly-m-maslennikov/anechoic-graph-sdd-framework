---
atom_family: SPEC
atom_id: AN-S-2621
structure:
  container:
    component: C15
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-11 15:29:41 +0400
---

## Summary

Declare CODEX_HOOK

## Claim

### Prose Claim

CODEX_HOOK owns the generic Codex command hook, its host installation and the context passed to ANECHOIC MCP. The hook works without a plugin. Workbench UI integration remains separate.

For local Atoms that define the host-adapter contract, the exact Main Subject is `MODEL//ANECHOIC <+ Atom`. It selects that declared object, not its descendants or other type members. The scope is this hook's ANECHOIC request binding. An unresolved target grants no admission.

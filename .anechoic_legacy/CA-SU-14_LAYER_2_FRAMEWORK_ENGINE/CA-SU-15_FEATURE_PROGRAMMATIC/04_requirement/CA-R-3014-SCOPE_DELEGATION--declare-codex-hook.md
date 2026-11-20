---
identity:
  atom_id: CA-R-3014
  ref_id: CA-R-3014
context:
  container:
    scope_unit: CA-SU-15
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//CODEX_HOOK
  tier: 3
state:
  status: Active
  version: 2
  updated_at: 2026-11-11 15:29:41 +0400
destination:
  file:
    name: CA-R-3014-SCOPE_DELEGATION--declare-codex-hook.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement
author: Anatoly Maslennikov
---

## Summary

Declare CODEX_HOOK

## Claim

### Prose Claim

CODEX_HOOK owns the generic Codex command hook, its host installation and the context passed to ANECHOIC MCP. The hook works without a plugin. Workbench UI integration remains separate.

For local Atoms that define the host-adapter contract, the exact Main Subject is `MODEL//ANECHOIC <+ Atom`. It selects that declared object, not its descendants or other type members. The scope is this hook's ANECHOIC request binding. An unresolved target grants no admission.

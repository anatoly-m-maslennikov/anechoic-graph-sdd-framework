---
atom_family: SPEC
atom_id: AN-S-2621
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Declare CODEX_HOOK

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//CODEX_HOOK.ID == "CA-SU-49";
Scope Unit//CODEX_HOOK.Name == "CODEX_HOOK";
Scope Unit//CODEX_HOOK.Label == "FEATURE";
Scope Unit//CODEX_HOOK.order.ordered == false;
Scope Unit//CODEX_HOOK ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```

### Prose Claim

CODEX_HOOK owns the generic Codex command hook, its host installation and the context passed to ANECHOIC MCP. The hook works without a plugin. Workbench UI integration remains separate.

Admit local Requirement/Requirement, Method/Decision, Evaluation/Eval Case and Delivery/Decision pairs for the host-adapter contract. Their exact HAS_ACTIVE_SUBJECT target is `MODEL//ANECHOIC <+ Atom`. It selects that declared object, not its descendants or other type members. Their precise Content Scope is this hook's ANECHOIC request binding. An unresolved target grants no admission. Existing default admissions remain unchanged.

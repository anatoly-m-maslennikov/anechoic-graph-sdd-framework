---
atom_family: SPEC
atom_id: AN-S-2994
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 14:23:38 +0400
---

## Summary

Declare WORKBENCH_CODEX

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_CODEX.ID == "CA-SU-47";
Scope Unit//WORKBENCH_CODEX.Name == "WORKBENCH_CODEX";
Scope Unit//WORKBENCH_CODEX.Label == "FEATURE";
Scope Unit//WORKBENCH_CODEX.order.ordered == false;
Scope Unit//WORKBENCH_CODEX ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```

### Prose Claim

Own Codex integration in Workbench: one chat per Project, its conversation interface, Project context, sessions and turns, streamed output, calls to all Tools exposed by the enabled configured MCP servers, and approval interaction. ANECHOIC calls carry the selected Project root; other servers retain their own inputs. Shared Workbench contracts remain in WORKBENCH.

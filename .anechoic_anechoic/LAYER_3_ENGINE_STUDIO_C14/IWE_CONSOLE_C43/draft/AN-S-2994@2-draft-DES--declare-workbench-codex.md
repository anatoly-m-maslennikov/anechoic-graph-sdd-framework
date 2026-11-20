---
identity:
  atom_id: AN-S-2994
context:
  container:
    component: C43
  tier: 3
  lens: DES
state:
  status: draft
  version: 2
  updated_at: 2026-11-05 16:45:35 +0400
---

## Summary

Declare WORKBENCH_CODEX

## Claim

### Prose Claim

Own Codex integration in Workbench: one chat per Project, its conversation interface, Project context, sessions and turns, streamed output, calls to all Tools exposed by the enabled configured MCP servers, and approval interaction. ANECHOIC calls carry the selected Project root; other servers retain their own inputs. Shared Workbench contracts remain in WORKBENCH.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='WORKBENCH_CODEX',
    instance=ScopeUnit(
        id='CA-SU-47',
        name='WORKBENCH_CODEX',
        label='FEATURE',
        ordered=False,
        container='WORKBENCH',
        structural_level=5,
    ),
)
```


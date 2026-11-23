---
atom_id: CA-R-2790
ref_id: CA-R-2790@2-draft
container:
  scope_unit: CA-SU-43
role: Requirement
form: Scope Unit Declaration
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH_CODEX
tier: 3
status: Draft
version: 2
updated_at: 2026-11-05 16:45:35 +0400
carrier_destination:
  file:
    name: CA-R-2790@2-draft-WORKBENCH-DEFINES_SCOPE_FOR-WORKBENCH_CODEX--declare-workbench-codex.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/04_requirement/000_draft
current_scope_unit: WORKBENCH
claim_target_scope_unit: WORKBENCH_CODEX
author: Anatoly Maslennikov
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


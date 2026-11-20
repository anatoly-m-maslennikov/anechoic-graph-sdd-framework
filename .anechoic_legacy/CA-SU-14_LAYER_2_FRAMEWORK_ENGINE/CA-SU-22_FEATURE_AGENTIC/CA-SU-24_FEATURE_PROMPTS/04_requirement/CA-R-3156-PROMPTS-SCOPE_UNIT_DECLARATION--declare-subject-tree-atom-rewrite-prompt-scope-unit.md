---
identity:
  atom_id: CA-R-3156
  ref_id: CA-R-3156
context:
  role: requirement
  form: scope_unit_declaration
  tier: 3
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//SUBJECT_TREE_ATOM_REWRITE_PROMPT
  container:
    scope_unit: CA-SU-24
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:44:45.142927+00:00'
destination:
  file:
    name: CA-R-3156-PROMPTS-SCOPE_UNIT_DECLARATION--declare-subject-tree-atom-rewrite-prompt-scope-unit.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/04_requirement
---
## Summary

Declare SUBJECT TREE ATOM REWRITE PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-56',
        name='SUBJECT_TREE_ATOM_REWRITE_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```

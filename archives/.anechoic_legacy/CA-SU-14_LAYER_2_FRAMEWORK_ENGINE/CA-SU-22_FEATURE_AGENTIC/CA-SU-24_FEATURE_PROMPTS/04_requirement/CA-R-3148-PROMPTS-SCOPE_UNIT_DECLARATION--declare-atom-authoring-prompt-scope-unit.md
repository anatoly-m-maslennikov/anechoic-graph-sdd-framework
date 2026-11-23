---
identity:
  atom_id: CA-R-3148
  ref_id: CA-R-3148
context:
  role: requirement
  form: scope_unit_declaration
  container:
    scope_unit: CA-SU-24
  tier: 3
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//ATOM_AUTHORING_PROMPT
state:
  version: 1
  status: active
  updated_at: '2026-11-13T17:58:24.609338+00:00'
destination:
  file:
    name: CA-R-3148-PROMPTS-SCOPE_UNIT_DECLARATION--declare-atom-authoring-prompt-scope-unit.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/04_requirement
---
## Summary

Declare ATOM AUTHORING PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='ATOM_AUTHORING_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-54',
        name='ATOM_AUTHORING_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```

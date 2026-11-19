---
identity:
  atom_id: CA-R-3159
  ref_id: CA-R-3159
context:
  role: requirement
  form: scope_unit_declaration
  tier: 3
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//SUBJECT_ATOM_GATHERER_PROMPT
  container:
    scope_unit: CA-SU-24
state:
  version: 1
  status: active
  updated_at: '2026-11-13T19:52:51.241737+00:00'
destination:
  file:
    name: CA-R-3159-PROMPTS-SCOPE_UNIT_DECLARATION--declare-subject-atom-gatherer-prompt-scope-unit.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-22_FEATURE_AGENTIC/CA-SU-24_FEATURE_PROMPTS/04_requirement
---
## Summary

Declare SUBJECT ATOM GATHERER PROMPT Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='SUBJECT_ATOM_GATHERER_PROMPT',
    instance=ScopeUnit(
        id='CA-SU-57',
        name='SUBJECT_ATOM_GATHERER_PROMPT',
        label='FEATURE',
        ordered=False,
        container='PROMPTS',
        structural_level=4,
    ),
)
```

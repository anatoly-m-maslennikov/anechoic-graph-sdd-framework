---
atom_family: SPEC
atom_id: AN-S-3049
container:
  component: C22
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 16
  updated_at: "2026-11-26T15:52:29.850220+00:00"
---

## Summary

Declare PROMPTS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C24',
    name='PROMPTS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['ADAPTERS_C30__shared.CarrierError',
                      'ADAPTERS_C30__shared.parse_carrier',
                      'FEATURE_TOOLS__tests__shared.load_candidate_schema',
                      'ADAPTERS_C30__shared.atomic_tempfile',
                      'carrier_read__pub.CarrierError',
                      'carrier_read__pub.parse_carrier',
                      'journal_settings__pub.configured_journal_root',
                      'work_journal__pub.append_sealed_events',
                      'repair_gate__shared.admit_proposal',
                      'repair_gate__shared.admit_layout_recoding',
                      'repair_gate__shared.admit_layout_preview',
                      'repair_gate__shared.admit_layout_subject_recoding',
                      'repair_gate__shared.admit_scope_extraction_preview',
                      'repair_gate__shared.admit_scope_extraction_subject_recoding',
                      'repair_gate__shared.admit_subject_recoding',
                      'repair_gate__shared.authority_digest'],
          'exports': {}}}
```

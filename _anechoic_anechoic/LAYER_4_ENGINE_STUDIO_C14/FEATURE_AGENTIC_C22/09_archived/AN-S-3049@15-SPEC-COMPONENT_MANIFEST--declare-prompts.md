---
atom_family: SPEC
atom_id: AN-S-3049
container:
  component: C22
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 15
  updated_at: "2026-11-26T15:54:01.171596+00:00"
---

## Summary

Declare PROMPTS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C24',
        name='PROMPTS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {'imports': [
                    'ADAPTERS_C30__shared.CarrierError',
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
                'repair_gate__shared.authority_digest',
            ], 'exports': {
            }},
        },
    ),
)
```

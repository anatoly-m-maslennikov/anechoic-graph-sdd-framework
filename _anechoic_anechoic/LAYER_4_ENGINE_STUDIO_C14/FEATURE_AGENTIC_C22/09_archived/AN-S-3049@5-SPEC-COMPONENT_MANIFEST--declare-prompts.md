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
  version: 5
  updated_at: "2026-11-22T15:27:08.128126+00:00"
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
                'project_temporary__pub.atomic_tempfile',
                'carrier_read__pub.CarrierError',
                'carrier_read__pub.parse_carrier',
                'journal_settings__pub.configured_journal_root',
                'work_journal__pub.append_sealed_events',
            ]},
            'io': {
                'server': {
                    'query_frozen_review_context': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/context_builder.py',
                        'arguments': ['--context', '<frozen-index-json>', '--query', '<text>'],
                    },
                },
            },
            'state': {
                'reads': ['admitted review inputs', 'frozen Entity context', 'configured Project Journal location'],
                'writes': ['review Run recovery cache and locks', 'Run evidence reports', 'confirmed Run events in the Project Journal'],
            },
        },
    ),
)
```

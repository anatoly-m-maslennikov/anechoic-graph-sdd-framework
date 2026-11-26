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
  status: draft
  version: 14
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
                    'RMED_ATOM_REVIEW__shared.GROUPS',
                    'RMED_ATOM_REVIEW__shared.LOCAL_GROUPS',
                    'RMED_ATOM_REVIEW__shared.ReviewContext',
                    'RMED_ATOM_REVIEW__shared._validate_resolved_mention',
                    'RMED_ATOM_REVIEW__shared._validate_subject_findings',
                    'RMED_ATOM_REVIEW__shared.authority_reference',
                    'RMED_ATOM_REVIEW__shared.body_section_texts',
                    'RMED_ATOM_REVIEW__shared.body_sections',
                    'RMED_ATOM_REVIEW__shared.groups_for',
                    'RMED_ATOM_REVIEW__shared.literal_occurs',
                    'RMED_ATOM_REVIEW__shared.lookup',
                    'RMED_ATOM_REVIEW__shared.markdown',
                    'RMED_ATOM_REVIEW__shared.merge_evaluations',
                    'RMED_ATOM_REVIEW__shared.metadata',
                    'RMED_ATOM_REVIEW__shared.prepare_context',
                    'RMED_ATOM_REVIEW__shared.probability',
                    'RMED_ATOM_REVIEW__shared.prose',
                    'RMED_ATOM_REVIEW__shared.rebuild_baseline',
                    'RMED_ATOM_REVIEW__shared.summarize_evaluations',
                    'RMED_ATOM_REVIEW__shared.text',
                    'RMED_ATOM_REVIEW__shared.validate_part',
                    'RMED_ATOM_REVIEW__shared.validate_quotes',
                    'RMED_ATOM_REVIEW__shared.validate_report_quality',
                    'RMED_ATOM_REVIEW__shared.validate_subject_inventory',
                    'ADAPTERS_C30__shared.CarrierError',
                    'ADAPTERS_C30__shared.parse_carrier',
                'FEATURE_TOOLS__tests__shared.load_candidate_schema',
                'ADAPTERS_C30__shared.atomic_tempfile',
                'carrier_read__pub.CarrierError',
                'carrier_read__pub.parse_carrier',
                'journal_settings__pub.configured_journal_root',
                'work_journal__pub.append_sealed_events',
                'RMED_ATOM_REVIEW__tests__shared.RULE_TEXT',
                'RMED_ATOM_REVIEW__tests__shared.SOURCE_TEXT',
                'RMED_ATOM_REVIEW__tests__shared.contract',
                'RMED_ATOM_REVIEW__tests__shared.gap',
                'RMED_ATOM_REVIEW__tests__shared.part',
                'RMED_ATOM_REVIEW__tests__shared.source',
                'repair_gate__shared.admit_proposal',
                'repair_gate__shared.admit_layout_recoding',
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

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
  status: "active"
  version: 6
  updated_at: "2026-11-22T15:27:08.129309+00:00"
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
                'RMED_ATOM_REVIEW__tests__shared.RULE_TEXT',
                'RMED_ATOM_REVIEW__tests__shared.SOURCE_TEXT',
                'RMED_ATOM_REVIEW__tests__shared.contract',
                'RMED_ATOM_REVIEW__tests__shared.gap',
                'RMED_ATOM_REVIEW__tests__shared.part',
                'RMED_ATOM_REVIEW__tests__shared.source',
                'repair_gate__shared.admit_proposal',
                'repair_gate__shared.admit_layout_recoding',
                'review_evidence__shared.markdown',
            ], 'exports': {
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.RULE_TEXT': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.SOURCE_TEXT': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.contract': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.gap': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.part': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared.source': {'private': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._path': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._summary': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._same_summary_value': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._permission': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._resolutions': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._outputs': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._updated_at': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._timestamp_normalized_header': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._refreshes_updated_at': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._recoding_identity': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._formatting_identity': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._removes_role_echo': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._role_echo_path': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._identity': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._output_binding': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._candidate_bindings': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._preflight': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared.admit_proposal': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared._local_repair_boundary': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared.admit_layout_recoding': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.ReviewContext': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared._validate_resolved_mention': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared._validate_subject_findings': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.literal_occurs': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.markdown': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/ACTION_PROMPTS/RMED_ATOM_REVIEW/repair/repair__tests']},
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.probability': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.strings': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.text': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.validate_obligations': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.validate_quotes': None,
                'ACTION_PROMPTS.RMED_ATOM_REVIEW.review_evidence__shared.validate_subject_inventory': None,
            }},
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

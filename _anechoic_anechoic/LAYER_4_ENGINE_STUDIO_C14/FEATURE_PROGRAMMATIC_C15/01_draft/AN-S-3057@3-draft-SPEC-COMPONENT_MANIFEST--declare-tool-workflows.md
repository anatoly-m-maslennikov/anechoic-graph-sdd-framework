---
atom_family: SPEC
atom_id: AN-S-3057
container:
  component: C15
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T12:24:22+00:00'
---

## Summary

Declare TOOL_WORKFLOWS

## Purpose

Own the sequencing and domain policy of a public logical Tool Workflow.
Resolve one responsible Workflow before executing any Action.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C18',
        name='TOOL_WORKFLOWS',
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'io': {
                'server': {
                    'run_tool_workflow': {
                        'outcomes': {
                            'workflow_completed': {'must_effect': [('actions', 'completed')], 'forbid_effect': ['action_stop']},
                            'failed': {
                                'must_effect': [('actions', 'dispatched'), ('action_stop', 'observed'),
                                                ('completed_effects', 'retained'), ('remaining_targets', 'untouched')],
                            },
                            'owner_resolution_failed': {'forbid_effect': ['actions']},
                        },
                    },
                },
            },
        },
    ),
)
```

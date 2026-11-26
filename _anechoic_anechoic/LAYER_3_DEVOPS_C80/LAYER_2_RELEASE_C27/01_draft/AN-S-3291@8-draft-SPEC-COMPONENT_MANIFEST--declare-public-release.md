---
atom_family: SPEC
atom_id: AN-S-3291
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 8
  updated_at: '2026-11-25T18:22:26.697241+00:00'
---

## Summary

Declare Public Release

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C64',
        name='Public Release',
        layer=3,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {
                'imports': {'only': ['C64']},
            },
            'io': {
                'server': {
                    'prepare_public_release': {'outcomes': {
                        'completed': {
                            'must_effect': [('git_base_head', 'resolved'), ('content_draft_commit_pins', 'matched'), ('release_drafts', 'rendered'), ('pull_request_description', 'returned'), ('version_history', 'returned')],
                            'forbid_effect': ['external_publish', 'checkout_write'],
                        },
                    }},
                    'public_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'command': 'public',
                    },
                },
                'client': [],
            },
            'state': {
                'reads': ['Git commits and completed Task and Epic Markdown', 'Public release content draft'],
                'writes': [],
            },
        },
    ),
)
```

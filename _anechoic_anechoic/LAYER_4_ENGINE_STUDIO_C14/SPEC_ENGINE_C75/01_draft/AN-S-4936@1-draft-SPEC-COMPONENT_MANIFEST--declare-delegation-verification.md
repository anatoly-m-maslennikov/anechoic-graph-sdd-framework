---
atom_family: SPEC
atom_id: AN-S-4936
container:
  component: C75
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Delegation Verification

## Purpose

Check parent, child, and sibling delegation relationships against the formal model.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C89',
        layer=5,
        name='Delegation Verification',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {
                'server': {
                    'check_child_outcome': {'outcomes': {
                        'compared': {'must_effect': [('C89.child_outcome_comparison', 'reported')]},
                    }},
                    'check_sibling_outcome': {'outcomes': {
                        'compared': {'must_effect': [('C89.sibling_outcome_comparison', 'reported')]},
                    }},
                },
            },
        },
    ),
)
```

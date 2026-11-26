---
atom_family: SPEC
atom_id: AN-S-3076
container:
  component: C31
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

Declare ATOM_ACTIONS

## Purpose

Apply a logical Atom Action to one explicitly selected Atom.
Keep selection, expected-state checking and change distinct.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C35',
        name='ATOM_ACTIONS',
        lens_whitelist=['DES', 'QA'],
        boundaries={
            'io': {
                'server': {
                    'replace_logical_atom_properties': {
                        'outcomes': {
                            'change_reported': {
                                'must_effect': [('logical_target', 'one_explicit'), ('selected_atom_value', 'read'),
                                                ('expected_state', 'checked'), ('change', 'completed'),
                                                ('unselected_content', 'preserved')],
                                'forbid_effect': ['semantic_target_substitution'],
                            },
                            'failure_reported': {
                                'must_effect': [('replacement_report', 'failure')],
                            },
                            'uncertainty_reported': {
                                'must_effect': [('replacement_report', 'uncertainty')],
                            },
                            'invalid_target_rejected': {
                                'must_effect': [('logical_target', 'invalid_cardinality')],
                                'forbid_effect': ['selected_atom_value', 'change', 'semantic_target_substitution'],
                            },
                            'stale_precondition_rejected': {
                                'must_effect': [('expected_state', 'mismatch')],
                                'forbid_effect': ['change', 'semantic_target_substitution'],
                            },
                        },
                    },
                },
            },
        },
    ),
)
```

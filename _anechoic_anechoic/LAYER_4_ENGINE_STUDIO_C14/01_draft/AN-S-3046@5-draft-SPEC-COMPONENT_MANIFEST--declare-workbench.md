---
atom_family: SPEC
atom_id: AN-S-3046
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: '2026-11-25T13:50:02.356115+00:00'
relations:
  CONTRIBUTES_TO:
  - AN-S-3330

---

## Summary

Declare WORKBENCH

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C43',
        name='WORKBENCH',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {'imports': []},
            'io': {
                'client': {'workbench': {'component': 'C21', 'interface': 'workbench_http'}},
                'server': {'workbench_run_view': {'outcomes': {'succeeded': {
                    'must_effect': [('C21.view_run.query_id', 'returned'), ('workbench_display', 'shown')],
                    'forbid_effect': ['workbench_save_error'],
                }, 'partial': {
                    'must_effect': [('C21.view_run.query_id', 'returned'), ('C21.view_run.save_error', 'returned'),
                                    ('workbench_save_error', 'shown'), ('workbench_display', 'shown')],
                }}}},
            },
            'state': {'reads': [], 'writes': []},
        },
    ),
)
```

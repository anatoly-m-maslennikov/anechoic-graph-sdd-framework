---
atom_family: SPEC
atom_id: AN-S-3082
structure:
  container:
    component: C43
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 2
  updated_at: "2026-11-21T12:14:05.597140+00:00"
---

## Summary

Declare IMPORT_GRAPH

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C61',
        name='IMPORT_GRAPH',
        lens_whitelist=['DES', 'QA', 'SWD'],
        boundaries={
            'code_access': {
                'imports': [],
                'exports': {
                    'import_graph__family_pub': None,
                    'import_graph__family_pub.ImportSite': None,
                    'import_graph__family_pub.Source': None,
                    'import_graph__family_pub.capture': None,
                    'import_graph__family_pub.relevant_change': None,
                    'import_graph__family_pub.resolve_realization': None,
                },
            },
        },
    ),
)
```

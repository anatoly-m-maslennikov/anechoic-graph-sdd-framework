---
atom_family: SPEC
atom_id: AN-S-3082
container:
  component: C43
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-22T01:14:11.526234+00:00"
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
            'code': {
                'imports': {'only': []},
                'exports': {
                    'import_graph__shared': None,
                    'import_graph__shared.ImportSite': None,
                    'import_graph__shared.Source': None,
                    'import_graph__shared.capture': None,
                    'import_graph__shared.excluded_source_path': None,
                    'import_graph__shared.event_path': None,
                    'import_graph__shared.git_ignored': None,
                    'import_graph__shared.iter_files': None,
                    'import_graph__shared.relative_path': None,
                    'import_graph__shared.relevant_change': None,
                    'import_graph__shared.resolve_realization': None,
                },
            },
        },
    ),
)
```

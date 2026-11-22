---
atom_family: SPEC
atom_id: AN-S-3334
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---
## Summary

Declare Workers Beta

## Purpose

Build a transient snapshot of Current Atoms for the selected Project.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C69',
        name='Workers Beta',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'imports': ['native_source_rows__pub.capture_native', 'markdown_content__pub.content_lines']}, 'io': {'server': {'atom_snapshot': {'transport': 'cli', 'runner': 'managed_python', 'path': 'LAYER_3_ENGINE_STUDIO_C14/WORKERS_beta_C69/WORKERS_beta_C69__pub.py', 'input': 'JSON Project binding on stdin', 'output': 'JSON Atom snapshot on stdout'}}}, 'state': {'reads': ['pinned Project Manifest and native Atom carriers'], 'writes': []}},
    ),
)
```

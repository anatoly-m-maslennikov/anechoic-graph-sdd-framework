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
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:00.972592+00:00"
---

## Summary

Declare TOOL_WORKFLOWS

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
    ),
)
```

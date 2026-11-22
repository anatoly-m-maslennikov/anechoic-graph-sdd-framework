---
atom_family: SPEC
atom_id: AN-S-3049
container:
  component: C22
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T02:36:18.340016+00:00"
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
    ),
)
```

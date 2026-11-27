---
atom_family: SPEC
atom_id: AN-S-3040
container:
  component: C82
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-26T15:54:00.657492+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-3328
---

## Summary

Declare Meta-ontology

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C9',
        name='Continuant Pitchfork',
        layer=1,
        lens_whitelist=['DES', 'DES/DOM', 'DOM/CONT', 'DOM/ONT', 'DevOps', 'QA', 'SWD'],
    ),
)
```

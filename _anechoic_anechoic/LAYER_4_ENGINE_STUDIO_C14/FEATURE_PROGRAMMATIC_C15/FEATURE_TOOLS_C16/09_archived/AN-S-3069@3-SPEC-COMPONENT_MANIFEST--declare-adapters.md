---
atom_family: SPEC
atom_id: AN-S-3069
container:
  component: C16
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T02:18:13.788478+00:00"
---

## Summary

Declare ADAPTERS

## Purpose

Provide guarded filesystem and YAML carrier input to Project Components.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C30',
        name='ADAPTERS',
        lens_whitelist=['SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'ADAPTERS_C30__pub.CEILINGS': 'public',
                    'ADAPTERS_C30__pub.LimitReached': 'public',
                    'ADAPTERS_C30__pub.ReadContext': 'public',
                    'ADAPTERS_C30__pub.ReadFailure': 'public',
                    'ADAPTERS_C30__pub.open_regular': 'public',
                    'ADAPTERS_C30__pub.protected': 'public',
                    'carrier_syntax__pub.CarrierError': 'public',
                    'carrier_syntax__pub.UniqueSafeLoader': 'public',
                    'carrier_syntax__pub.check_yaml_resources': 'public',
                    'carrier_syntax__pub.parse_carrier_syntax': 'public',
                },
            },
        },
    ),
)
```

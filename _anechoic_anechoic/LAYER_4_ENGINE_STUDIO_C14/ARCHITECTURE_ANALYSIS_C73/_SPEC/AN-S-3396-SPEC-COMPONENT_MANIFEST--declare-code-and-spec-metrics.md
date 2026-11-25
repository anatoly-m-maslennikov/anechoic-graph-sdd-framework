---
atom_family: SPEC
atom_id: AN-S-3396
container:
  component: C73
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---
## Summary

Declare Code and Spec Metrics

## Purpose

Measure code and Spec against the admitted Project snapshot. Provide size and dependency evidence for Package boundary review.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C76',
        name='Code and Spec Metrics',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'code': {
                'imports': ['metrics__shared.code_rows', 'metrics__shared.spec_rows'],
            },
            'state': {'reads': ['captured code inventory and Current Spec measurements'], 'writes': []},
        },
    ),
)
```

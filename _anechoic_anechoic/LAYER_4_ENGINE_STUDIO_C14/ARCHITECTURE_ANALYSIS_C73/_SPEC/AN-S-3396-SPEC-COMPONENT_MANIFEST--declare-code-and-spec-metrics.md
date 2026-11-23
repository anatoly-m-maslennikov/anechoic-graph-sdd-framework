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
  version: 1
  updated_at: '2026-11-23T04:32:26.395669+00:00'
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
                'exports': {
                    'metrics__shared.code_rows': {'shared': [
                        'C69',
                        'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/CODE_AND_SPEC_METRICS_C76/CODE_AND_SPEC_METRICS_C76__tests',
                    ]},
                    'metrics__shared.spec_rows': {'shared': [
                        'C30',
                        'LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/CODE_AND_SPEC_METRICS_C76/CODE_AND_SPEC_METRICS_C76__tests',
                    ]},
                    'metrics__shared.is_measurement_input': {'shared': ['C61', 'C68']},
                },
            },
        },
    ),
)
```
